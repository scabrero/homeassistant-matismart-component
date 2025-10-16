"""Base entity for the Matismart integration."""

from __future__ import annotations

import logging

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from pymatis.properties import MatisProperty as mp

from .const import DEFAULT_NAME, DOMAIN
from .coordinator import MatisDataUpdateCoordinator

LOGGER = logging.getLogger(__name__)


class MatisEntity(CoordinatorEntity[MatisDataUpdateCoordinator]):
    """Defines a base Matis entity."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: MatisDataUpdateCoordinator,
        entity_description: EntityDescription,
    ) -> None:
        """Initialize Matis entity."""
        super().__init__(coordinator)
        device_address = coordinator.data[mp.MODBUS_ADDRESS]
        hardware_id = coordinator.data[mp.HARDWARE_ID]
        firmware = coordinator.data[mp.FIRMWARE_VERSION]
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_address)},
            manufacturer=DEFAULT_NAME,
            name=f"{hardware_id}@{device_address}",
            model=f"{hardware_id}",
            model_id=f"0x{hardware_id:04X}",
            sw_version=f"0x{firmware:04X}",
        )
        self.entity_description = entity_description
        self._attr_unique_id = (
            f"{hardware_id}_{device_address}_{entity_description.key}"
        )
        LOGGER.debug(self._attr_unique_id)
