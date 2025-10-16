"""Binary sensor platform for the Matismart integration."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable, Literal

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.typing import StateType
from pymatis.constants import MatisHardwareId
from pymatis.properties import MatisProperty as mp

from custom_components.matismart.entity import MatisEntity

from . import MatisConfigEntry
from .coordinator import MatisDataUpdateCoordinator

LOGGER = logging.getLogger(__name__)

# Uses coordinator
PARALLEL_UPDATES = 0


@dataclass(frozen=True, kw_only=True)
class MatisBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Matis sensor description."""

    value_fn: Callable[[Any], StateType]
    on_state: Literal[True, False]

    def __post_init__(self):
        """Defaults the translation_key to the sensor key."""

        # special setter to be able to set/update the translation_key in this frozen dataclass.
        # cfr. https://docs.python.org/3/library/dataclasses.html#frozen-instances
        object.__setattr__(
            self,
            "translation_key",
            self.translation_key or self.key.replace("-", "_").lower(),
        )


MT53RA_SX_BINARY_SENSOR_ENTITIES: tuple[MatisBinarySensorEntityDescription, ...] = (
    MatisBinarySensorEntityDescription(
        key=str(mp.AUX_OUTPUT_STATUS),
        device_class=BinarySensorDeviceClass.OPENING,
        on_state=False,
        value_fn=lambda data: data[mp.AUX_OUTPUT_STATUS],
    ),
    MatisBinarySensorEntityDescription(
        key=str(mp.PADLOCK_STATUS),
        device_class=BinarySensorDeviceClass.LOCK,
        on_state=False,
        value_fn=lambda data: data[mp.PADLOCK_STATUS],
    ),
)


class MatisBinarySensorEntity(MatisEntity, BinarySensorEntity):  # type: ignore[override]
    """Matis sensor."""

    entity_description: MatisBinarySensorEntityDescription

    def __init__(
        self,
        description: MatisBinarySensorEntityDescription,
        coordinator: MatisDataUpdateCoordinator,
    ) -> None:
        """Initialize the Matis sensor entity."""
        super().__init__(coordinator, description)
        self.entity_description = description  # type: ignore[override]

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle update data from the coordinator."""
        LOGGER.debug(
            "Handle update for binary sensor %s",
            self.entity_description.key,
        )
        data = self.coordinator.data
        self._attr_is_on = (
            self.entity_description.value_fn(data) == self.entity_description.on_state
        )
        self.async_write_ha_state()


async def async_setup_entry(
    hass: HomeAssistant,  # pylint: disable=unused-argument
    entry: MatisConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the sensors."""
    entities: list[BinarySensorEntity] = []
    coordinator: MatisDataUpdateCoordinator = entry.runtime_data
    hardware_id = coordinator.data[mp.HARDWARE_ID]
    if hardware_id == MatisHardwareId.MT53RA_SX:
        entities.extend(
            [
                MatisBinarySensorEntity(description, coordinator)
                for description in MT53RA_SX_BINARY_SENSOR_ENTITIES
            ]
        )
    async_add_entities(entities)
