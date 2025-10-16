"""Sensor platform for the Matismart integration."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    EntityCategory,
    UnitOfTime,
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
class MatisSensorEntityDescription(SensorEntityDescription):
    """Matis sensor description."""

    value_fn: Callable[[Any], StateType]

    def __post_init__(self):
        """Defaults the translation_key to the sensor key."""

        # special setter to be able to set/update the translation_key in this frozen dataclass.
        # cfr. https://docs.python.org/3/library/dataclasses.html#frozen-instances
        object.__setattr__(
            self,
            "translation_key",
            self.translation_key or self.key.replace("-", "_").lower(),
        )


MT53RA_SX_SENSOR_ENTITIES: tuple[MatisSensorEntityDescription, ...] = (
    MatisSensorEntityDescription(
        key=str(mp.SYSTEM_CLOCK),
        entity_category=EntityCategory.DIAGNOSTIC,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        suggested_unit_of_measurement=UnitOfTime.DAYS,
        value_fn=lambda data: data[mp.SYSTEM_CLOCK].total_seconds(),
    ),
    MatisSensorEntityDescription(
        key=str(mp.DISPLAY_STATUS),
        value_fn=lambda data: str(data[mp.DISPLAY_STATUS]),
    ),
    MatisSensorEntityDescription(
        key=str(mp.HANDLE_LOCATION),
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: ", ".join(
            item.capitalize()
            for item in str(data[mp.HANDLE_LOCATION])
            .replace("LocationHall.", "")
            .split("|")
        ),
    ),
    MatisSensorEntityDescription(
        key=str(mp.COMMAND_CLOSING_TIMES),
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.TOTAL,
        value_fn=lambda data: data[mp.COMMAND_CLOSING_TIMES],
    ),
    MatisSensorEntityDescription(
        key=str(mp.COMMAND_OPENING_TIMES),
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.TOTAL,
        value_fn=lambda data: data[mp.COMMAND_OPENING_TIMES],
    ),
    MatisSensorEntityDescription(
        key=str(mp.MANUAL_PADLOCK_TIMES),
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.TOTAL,
        value_fn=lambda data: data[mp.MANUAL_PADLOCK_TIMES],
    ),
    MatisSensorEntityDescription(
        key=str(mp.MANUAL_CLOSING_TIMES),
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.TOTAL,
        value_fn=lambda data: data[mp.MANUAL_CLOSING_TIMES],
    ),
    MatisSensorEntityDescription(
        key=str(mp.AR_STATUS),
        value_fn=lambda data: ", ".join(
            item.capitalize()
            for item in str(data[mp.AR_STATUS])
            .replace("ReclosingStatus.", "")
            .replace("_", " ")
            .split("|")
        ),
    ),
    MatisSensorEntityDescription(
        key=str(mp.AR_CURRENT_ATTEMPT),
        state_class=SensorStateClass.TOTAL,
        value_fn=lambda data: data[mp.AR_CURRENT_ATTEMPT],
    ),
    MatisSensorEntityDescription(
        key=str(mp.AR_TIMER),
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        suggested_unit_of_measurement=UnitOfTime.MINUTES,
        value_fn=lambda data: data[mp.AR_TIMER].total_seconds(),
    ),
    MatisSensorEntityDescription(
        key=str(mp.AR_EXHAUSTED_TIMER),
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        suggested_unit_of_measurement=UnitOfTime.MINUTES,
        value_fn=lambda data: data[mp.AR_EXHAUSTED_TIMER].total_seconds(),
    ),
)


class MatisSensorEntity(MatisEntity, SensorEntity):  # type: ignore[override]
    """Matis sensor."""

    entity_description: MatisSensorEntityDescription

    def __init__(
        self,
        description: MatisSensorEntityDescription,
        coordinator: MatisDataUpdateCoordinator,
    ) -> None:
        """Initialize the Matis sensor entity."""
        super().__init__(coordinator, description)
        self.entity_description = description  # type: ignore[override]

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle update data from the coordinator."""
        LOGGER.debug(
            "Handle update for sensor %s",
            self.entity_description.key,
        )
        data = self.coordinator.data
        self._attr_native_value = self.entity_description.value_fn(data)
        self._attr_available = self._attr_native_value is not None
        self.async_write_ha_state()


async def async_setup_entry(
    hass: HomeAssistant,  # pylint: disable=unused-argument
    entry: MatisConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the sensors."""
    entities: list[SensorEntity] = []
    coordinator: MatisDataUpdateCoordinator = entry.runtime_data
    hardware_id = coordinator.data[mp.HARDWARE_ID]
    if hardware_id == MatisHardwareId.MT53RA_SX:
        entities.extend(
            [
                MatisSensorEntity(description, coordinator)
                for description in MT53RA_SX_SENSOR_ENTITIES
            ]
        )
    async_add_entities(entities)
