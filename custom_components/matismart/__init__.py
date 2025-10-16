"""The Matis integration."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_ADDRESS,
    CONF_DEVICE,
    CONF_HOST,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_TYPE,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryError, ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr
from pymatis.client import MatisBaseTransport, MatisRtuTransport, MatisTcpTransport
from pymatis.exceptions import MatisException
from pymatis.factory import factory as matis_factory
from pymatis.properties import MatisProperty as mp

from .const import (
    CONF_HARDWARE_ID,
    CONF_SERIAL_BAUDRATE,
    CONF_SERIAL_PARITY,
    CONF_SERIAL_STOPBITS,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    DeviceType,
)
from .coordinator import MatisDataUpdateCoordinator

LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.NUMBER,
    Platform.SWITCH,
]

type MatisConfigEntry = ConfigEntry[MatisDataUpdateCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: MatisConfigEntry) -> bool:  # pylint: disable=too-many-locals
    """Set up from a config entry."""
    transport: MatisBaseTransport | None = None
    device_type = entry.data[CONF_TYPE]
    if device_type == DeviceType.SERIAL:
        device = entry.data[CONF_DEVICE]
        baudrate = entry.data[CONF_SERIAL_BAUDRATE]
        parity = entry.data[CONF_SERIAL_PARITY]
        stop = entry.data[CONF_SERIAL_STOPBITS]
        transport = MatisRtuTransport(
            device, baudrate=baudrate, parity=parity, stop_bits=stop
        )
    elif device_type == DeviceType.NETWORK:
        host = entry.data[CONF_HOST]
        port = entry.data[CONF_PORT]
        transport = MatisTcpTransport(host, port)
    else:
        msg = f"Unexpected device type {device_type}"
        raise ConfigEntryError(msg)

    try:
        conf_model = entry.data[CONF_HARDWARE_ID]
    except ValueError as ex:
        message = "Failed to parse config model ID"
        raise ConfigEntryNotReady(message) from ex

    conf_address = entry.data[CONF_ADDRESS]

    try:
        api = matis_factory.get_device_by_model_id(conf_model, transport, conf_address)
        hardware_id = await api.get(mp.HARDWARE_ID)

        if hardware_id != conf_model:
            message = f"Unexpected device {hardware_id} found, expected {conf_model}"
            LOGGER.error(message)
            raise ConfigEntryError(message)
    except MatisException as ex:
        raise ConfigEntryNotReady from ex

    firmware = await api.get(mp.FIRMWARE_VERSION)
    update_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    coordinator = MatisDataUpdateCoordinator(hass, api, update_interval)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    entry.async_on_unload(entry.add_update_listener(update_listener))

    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, conf_address)},
        manufacturer=DEFAULT_NAME,
        name=f"{hardware_id}@{conf_address}",
        model=f"{hardware_id}",
        model_id=f"0x{hardware_id:04X}",
        sw_version=f"0x{firmware:04X}",
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def update_listener(hass: HomeAssistant, entry: MatisConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: MatisConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        coordinator: MatisDataUpdateCoordinator = entry.runtime_data
        coordinator.api.close()
    return unload_ok
