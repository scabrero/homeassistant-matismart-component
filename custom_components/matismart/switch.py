"""Switch platform for the Matismart integration."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Awaitable, Callable

from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntity,
    SwitchEntityDescription,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from pymatis.constants import Command, LocationHall, MatisHardwareId
from pymatis.device import MatisDevice
from pymatis.properties import MatisProperty as mp

from . import MatisConfigEntry
from .coordinator import MatisDataUpdateCoordinator, MatisDeviceData
from .entity import MatisEntity

LOGGER = logging.getLogger(__name__)

# Uses coordinator
PARALLEL_UPDATES = 0


@dataclass(frozen=True, kw_only=True)
class MatisSwitchEntityDescription(SwitchEntityDescription):
    """Matis sensor description."""

    is_on_fn: Callable[[MatisDeviceData], bool]
    set_state_fn: Callable[[MatisDevice, bool], Awaitable[bool]]

    def __post_init__(self):
        """Defaults the translation_key to the sensor key."""

        # special setter to be able to set/update the translation_key in this frozen dataclass.
        # cfr. https://docs.python.org/3/library/dataclasses.html#frozen-instances
        object.__setattr__(
            self,
            "translation_key",
            self.translation_key or self.key.replace("-", "_").lower(),
        )


MT53RA_SX_SWITCH_ENTITIES: tuple[MatisSwitchEntityDescription, ...] = (
    MatisSwitchEntityDescription(
        key=str(mp.CONTROL),
        device_class=SwitchDeviceClass.SWITCH,
        is_on_fn=lambda data: LocationHall.CLOSED in data[mp.HANDLE_LOCATION],
        set_state_fn=lambda device, state: device.set(mp.CONTROL, Command.CLOSE)
        if state
        else device.set(mp.CONTROL, Command.OPEN),
    ),
)


class MatisSwitchEntity(MatisEntity, SwitchEntity):  # type: ignore[override] # pylint: disable=abstract-method
    """Matis switch."""

    entity_description: MatisSwitchEntityDescription

    def __init__(
        self,
        description: MatisSwitchEntityDescription,
        coordinator: MatisDataUpdateCoordinator,
    ) -> None:
        """Initialize the Matis sensor entity."""
        super().__init__(coordinator, description)
        self.entity_description = description  # type: ignore[override]

    async def async_turn_off(self, **kwargs: Any) -> None:  # pylint: disable=unused-argument
        if await self.entity_description.set_state_fn(self.coordinator.api, False):
            self._attr_is_on = False
            self.async_write_ha_state()

    async def async_turn_on(self, **kwargs: Any) -> None:  # pylint: disable=unused-argument
        if await self.entity_description.set_state_fn(self.coordinator.api, True):
            self._attr_is_on = True
            self.async_write_ha_state()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle update data from the coordinator."""
        LOGGER.debug(
            "Handle update for switch %s",
            self.entity_description.key,
        )
        data = self.coordinator.data
        self._attr_is_on = self.entity_description.is_on_fn(data)
        self._attr_available = self._attr_is_on is not None
        self.async_write_ha_state()


async def async_setup_entry(
    hass: HomeAssistant,  # pylint: disable=unused-argument
    entry: MatisConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the sensors."""
    entities: list[SwitchEntity] = []
    coordinator: MatisDataUpdateCoordinator = entry.runtime_data
    hardware_id = coordinator.data[mp.HARDWARE_ID]
    if hardware_id == MatisHardwareId.MT53RA_SX:
        entities.extend(
            [
                MatisSwitchEntity(description, coordinator)
                for description in MT53RA_SX_SWITCH_ENTITIES
            ]
        )
    async_add_entities(entities)
