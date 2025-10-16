"""Config flow for the Matismart integration."""

from __future__ import annotations

import logging
from types import MappingProxyType
from typing import Any, Self

import homeassistant.helpers.config_validation as cv
import serial
import serial.tools.list_ports
import voluptuous as vol
from homeassistant.components import usb
from homeassistant.config_entries import (
    SOURCE_RECONFIGURE,
    SOURCE_USER,
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import (
    CONF_ADDRESS,
    CONF_DEVICE,
    CONF_HOST,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_TYPE,
)
from homeassistant.core import callback
from homeassistant.data_entry_flow import section
from homeassistant.exceptions import HomeAssistantError
from pymatis.client import MatisRtuTransport, MatisTcpTransport
from pymatis.constants import Baudrate, MatisHardwareId, Parity, SerialConfig, StopBits
from pymatis.exceptions import MatisException
from pymatis.factory import factory as matis_factory
from pymatis.properties import MatisProperty as mp

from .const import (
    CONF_DEFAULT_BAUDRATE,
    CONF_DEFAULT_HOST,
    CONF_DEFAULT_MODBUS_ADDRESS,
    CONF_DEFAULT_PARITY,
    CONF_DEFAULT_PORT,
    CONF_DEFAULT_STOPBITS,
    CONF_HARDWARE_ID,
    CONF_SERIAL_BAUDRATE,
    CONF_SERIAL_CONFIG,
    CONF_SERIAL_PARITY,
    CONF_SERIAL_STOPBITS,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    DeviceType,
)

CONF_MANUAL_PATH = "Enter Manually"

LOGGER = logging.getLogger(__name__)


class MatisConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Matismart."""

    # The schema version of the entries that it creates
    # Home Assistant will call your migrate method if the version changes
    VERSION = 1
    MINOR_VERSION = 1

    _reconfigure_data: MappingProxyType[str, Any]
    _modbus_address: int
    _serial_baudrate: Baudrate
    _serial_parity: Parity
    _serial_stopbits: StopBits
    _hardware_id: MatisHardwareId

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,  # noqa: ARG002
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._hardware_id = user_input[CONF_HARDWARE_ID]
            return await self.async_step_connection_type()

        supported_devices = {
            MatisHardwareId.MT53RA_SX: "MT53RAsx",
        }
        schema = vol.Schema(
            {
                vol.Required(CONF_HARDWARE_ID): vol.In(supported_devices),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_connection_type(
        self,
        user_input: dict[str, Any] | None = None,  # pylint: disable=unused-argument
    ) -> ConfigFlowResult:
        """Handle the connection_type step."""
        return self.async_show_menu(
            step_id="connection_type",
            menu_options=["serial", "network"],
        )

    async def _finish(self, entry_data: dict[str, Any]) -> ConfigFlowResult:
        model = str(entry_data[CONF_HARDWARE_ID])
        if self.source == SOURCE_USER:
            return self.async_create_entry(
                title=f"Matismart {model}",
                data=entry_data,
            )
        if self.source == SOURCE_RECONFIGURE:
            return self.async_update_reload_and_abort(
                self._get_reconfigure_entry(),
                data=entry_data,
            )
        msg = f"Unknown config flow source {self.source}"
        raise HomeAssistantError(msg)

    async def async_step_network(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Step when setting up a network device."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input[CONF_PORT]
            modbus_address = user_input[CONF_ADDRESS]
            try:
                data = await self._async_validate_network_device(
                    host=host,
                    port=port,
                    modbus_address=modbus_address,
                    model=self._hardware_id,
                )
            except UnexpectedHardwareIdError:
                errors["base"] = "unexpected_hardware_id"
            except MatisException:
                errors["base"] = "cannot_connect"
            else:
                return await self._finish(data)

        conf_host = CONF_DEFAULT_HOST
        conf_port = CONF_DEFAULT_PORT
        conf_modbus_address = CONF_DEFAULT_MODBUS_ADDRESS
        if self.source == SOURCE_RECONFIGURE:
            if hasattr(self._reconfigure_data, CONF_HOST):
                conf_host = self._reconfigure_data[CONF_HOST]
            if hasattr(self._reconfigure_data, CONF_PORT):
                conf_port = self._reconfigure_data[CONF_PORT]
            if hasattr(self._reconfigure_data, CONF_ADDRESS):
                conf_modbus_address = self._reconfigure_data[CONF_ADDRESS]
        schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default=conf_host): str,
                vol.Required(CONF_PORT, default=conf_port): cv.port,
                vol.Required(CONF_ADDRESS, default=conf_modbus_address): int,
            }
        )
        return self.async_show_form(
            step_id="network",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_serial(  # pylint: disable=too-many-locals
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Step when setting up serial configuration."""
        errors: dict[str, str] = {}

        if user_input is not None:
            LOGGER.debug(user_input)
            baudrate = user_input[CONF_SERIAL_CONFIG][CONF_SERIAL_BAUDRATE]
            parity = user_input[CONF_SERIAL_CONFIG][CONF_SERIAL_PARITY]
            stopbits = user_input[CONF_SERIAL_CONFIG][CONF_SERIAL_STOPBITS]
            modbus_address = user_input[CONF_ADDRESS]
            user_selection = user_input[CONF_DEVICE]
            if user_selection == CONF_MANUAL_PATH:
                self._modbus_address = modbus_address
                self._serial_baudrate = baudrate
                self._serial_parity = parity
                self._serial_stopbits = stopbits
                return await self.async_step_serial_manual_path()

            dev_path = await self.hass.async_add_executor_job(
                usb.get_serial_by_id, user_selection
            )
            try:
                sc = SerialConfig(
                    Baudrate(baudrate), Parity(parity), StopBits(stopbits)
                )
                data = await self._async_validate_serial_device(
                    device=dev_path,
                    serial_config=sc,
                    modbus_address=modbus_address,
                    model=self._hardware_id,
                )
            except UnexpectedHardwareIdError:
                errors["base"] = "unexpected_hardware_id"
            except MatisException:
                errors["base"] = "cannot_connect"
            else:
                return await self._finish(data)

        ports = await self.hass.async_add_executor_job(serial.tools.list_ports.comports)
        list_of_ports = {
            port.device: usb.human_readable_device_name(
                port.device,
                port.serial_number,
                port.manufacturer,
                port.description,
                f"{port.vid}" if port.vid else None,
                f"{port.pid}" if port.pid else None,
            )
            for port in ports
        }

        list_of_ports[CONF_MANUAL_PATH] = CONF_MANUAL_PATH
        conf_device = vol.UNDEFINED
        conf_modbus_address = CONF_DEFAULT_MODBUS_ADDRESS
        conf_serial_baudrate = CONF_DEFAULT_BAUDRATE
        conf_serial_parity = CONF_DEFAULT_PARITY
        conf_serial_stopbits = CONF_DEFAULT_STOPBITS
        if self.source == SOURCE_RECONFIGURE:
            if hasattr(self._reconfigure_data, CONF_DEVICE):
                conf_device = self._reconfigure_data[CONF_DEVICE]
            if hasattr(self._reconfigure_data, CONF_SERIAL_BAUDRATE):
                conf_serial_baudrate = self._reconfigure_data[CONF_SERIAL_BAUDRATE]
            if hasattr(self._reconfigure_data, CONF_SERIAL_PARITY):
                conf_serial_parity = self._reconfigure_data[CONF_SERIAL_PARITY]
            if hasattr(self._reconfigure_data, CONF_SERIAL_STOPBITS):
                conf_serial_stopbits = self._reconfigure_data[CONF_SERIAL_STOPBITS]
            if hasattr(self._reconfigure_data, CONF_ADDRESS):
                conf_modbus_address = self._reconfigure_data[CONF_ADDRESS]

        baudrate_opts = {
            Baudrate.BAUD_2400: "2400",
            Baudrate.BAUD_4800: "4800",
            Baudrate.BAUD_9600: "9600",
        }
        parity_opts = {
            Parity.PARITY_ODD: "Odd",
            Parity.PARITY_EVEN: "Even",
            Parity.PARITY_NONE: "None",
        }
        stop_bits_opts = {
            StopBits.STOP_1: "1",
            StopBits.STOP_2: "2",
        }

        schema = vol.Schema(
            {
                vol.Required(CONF_DEVICE, default=conf_device): vol.In(list_of_ports),
                vol.Required(CONF_ADDRESS, default=conf_modbus_address): int,
                vol.Required(CONF_SERIAL_CONFIG): section(
                    vol.Schema(
                        {
                            vol.Required(
                                CONF_SERIAL_BAUDRATE, default=conf_serial_baudrate
                            ): vol.In(baudrate_opts),
                            vol.Required(
                                CONF_SERIAL_PARITY, default=conf_serial_parity
                            ): vol.In(parity_opts),
                            vol.Required(
                                CONF_SERIAL_STOPBITS, default=conf_serial_stopbits
                            ): vol.In(stop_bits_opts),
                        }
                    ),
                    {"collapsed": True},
                ),
            }
        )
        return self.async_show_form(
            step_id="serial",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_serial_manual_path(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Select path manually."""
        errors: dict[str, str] = {}

        if user_input is not None:
            baudrate = self._serial_baudrate
            parity = self._serial_parity
            stopbits = self._serial_stopbits
            modbus_address = self._modbus_address
            device = user_input[CONF_DEVICE]
            try:
                sc = SerialConfig(
                    Baudrate(baudrate), Parity(parity), StopBits(stopbits)
                )
                data = await self._async_validate_serial_device(
                    device=device,
                    serial_config=sc,
                    modbus_address=modbus_address,
                    model=self._hardware_id,
                )
            except UnexpectedHardwareIdError:
                errors["base"] = "unknown_hardware_id"
            except MatisException:
                errors["base"] = "cannot_connect"
            else:
                return await self._finish(data)

        conf_device = vol.UNDEFINED
        if self.source == SOURCE_RECONFIGURE and hasattr(
            self._reconfigure_data, CONF_DEVICE
        ):
            conf_device = self._reconfigure_data[CONF_DEVICE]

        schema = vol.Schema({vol.Required(CONF_DEVICE, default=conf_device): str})
        return self.async_show_form(
            step_id="serial_manual_path",
            data_schema=schema,
            errors=errors,
        )

    async def _async_validate_unique_id(self, address: int) -> None:
        await self.async_set_unique_id(f"{address}")
        if self.source == SOURCE_USER:
            self._abort_if_unique_id_configured()
        if self.source == SOURCE_RECONFIGURE:
            self._abort_if_unique_id_mismatch()

    async def _async_validate_serial_device(
        self,
        device: str,
        serial_config: SerialConfig,
        modbus_address: int,
        model: MatisHardwareId,
    ) -> dict[str, Any]:
        await self._async_validate_unique_id(modbus_address)
        transport = MatisRtuTransport(
            device=device,
            baudrate=serial_config.baudrate,
            parity=serial_config.parity,
            stop_bits=serial_config.stop_bits,
        )

        mdev = matis_factory.get_device_by_model_id(
            model,
            transport,
            modbus_address,
        )

        hardware_id = await mdev.get(mp.HARDWARE_ID)
        if hardware_id != model:
            raise UnexpectedHardwareIdError

        data: dict[str, Any] = {
            CONF_TYPE: DeviceType.SERIAL,
            CONF_DEVICE: device,
            CONF_SERIAL_BAUDRATE: serial_config.baudrate,
            CONF_SERIAL_PARITY: serial_config.parity,
            CONF_SERIAL_STOPBITS: serial_config.stop_bits,
            CONF_ADDRESS: modbus_address,
            CONF_HARDWARE_ID: hardware_id,
        }
        return data

    async def _async_validate_network_device(
        self,
        host: str,
        port: int,
        modbus_address: int,
        model: MatisHardwareId,
    ) -> dict[str, Any]:
        await self._async_validate_unique_id(modbus_address)

        transport = MatisTcpTransport(host=host, port=port)

        mdev = matis_factory.get_device_by_model_id(
            model,
            transport,
            modbus_address,
        )

        hardware_id = await mdev.get(mp.HARDWARE_ID)
        if hardware_id != model:
            raise UnexpectedHardwareIdError

        data: dict[str, Any] = {
            CONF_TYPE: DeviceType.NETWORK,
            CONF_HOST: host,
            CONF_PORT: port,
            CONF_ADDRESS: modbus_address,
            CONF_HARDWARE_ID: hardware_id,
        }
        return data

    async def async_step_reconfigure(
        self,
        user_input: dict[str, Any] | None = None,  # pylint: disable=unused-argument
    ) -> ConfigFlowResult:
        """Handle reconfiguration."""
        self._reconfigure_data = self._get_reconfigure_entry().data
        return await self.async_step_user()

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:  # noqa: ARG004
        """Get the options flow for this handler."""
        return OptionsFlowHandler()

    def is_matching(self, other_flow: Self) -> bool:
        """Return True if other_flow is matching this flow."""
        return (
            other_flow._hardware_id == self._hardware_id  # pylint: disable=protected-access
            and other_flow._modbus_address == self._modbus_address  # pylint: disable=protected-access
        )


class OptionsFlowHandler(OptionsFlow):
    """Handle the options flow for Airios."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        scan_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )

        opts_schema = vol.Schema(
            {
                vol.Required(CONF_SCAN_INTERVAL, default=scan_interval): vol.All(
                    vol.Coerce(int), vol.Range(min=5, max=150)
                )
            }
        )
        return self.async_show_form(step_id="init", data_schema=opts_schema)


class UnexpectedHardwareIdError(HomeAssistantError):
    """Error to indicate unexpected hardware ID."""
