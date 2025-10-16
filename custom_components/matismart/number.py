"""Number platform for the Matismart integration."""

from __future__ import annotations

import math
import logging
from dataclasses import dataclass
from typing import Any, Awaitable, Callable

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.const import EntityCategory, UnitOfTime
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from pymatis.constants import MatisHardwareId
from pymatis.device import MatisDevice
from pymatis.properties import MatisProperty as mp

from . import MatisConfigEntry
from .coordinator import MatisDataUpdateCoordinator
from .entity import MatisEntity

LOGGER = logging.getLogger(__name__)

# Uses coordinator
PARALLEL_UPDATES = 0


@dataclass(frozen=True, kw_only=True)
class MatisNumberEntityDescription(NumberEntityDescription):
    """Matis number description."""

    value_fn: Callable[[Any], int]
    set_value_fn: Callable[[MatisDevice, int], Awaitable[bool]]

    def __post_init__(self):
        """Defaults the translation_key to the sensor key."""

        # special setter to be able to set/update the translation_key in this frozen dataclass.
        # cfr. https://docs.python.org/3/library/dataclasses.html#frozen-instances
        object.__setattr__(
            self,
            "translation_key",
            self.translation_key or self.key.replace("-", "_").lower(),
        )


MT53RA_SX_NUMBER_ENTITIES: tuple[MatisNumberEntityDescription, ...] = (
    MatisNumberEntityDescription(
        key=str(mp.AR_TOTAL_ATTEMPTS),
        native_max_value=10,
        native_min_value=1,
        native_step=1,
        mode=NumberMode.SLIDER,
        entity_category=EntityCategory.CONFIG,
        value_fn=lambda data: data[mp.AR_TOTAL_ATTEMPTS],
        set_value_fn=lambda device, value: device.set(mp.AR_TOTAL_ATTEMPTS, int(value)),
    ),
    MatisNumberEntityDescription(
        key=str(mp.AR_WAIT_TIME_1),
        native_max_value=3599,
        native_min_value=5,
        native_step=5,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        value_fn=lambda data: math.floor(data[mp.AR_WAIT_TIME_1].total_seconds()),
        set_value_fn=lambda device, value: device.set(mp.AR_WAIT_TIME_1, value),
    ),
    MatisNumberEntityDescription(
        key=str(mp.AR_STABLE_TIME_1),
        native_max_value=3599,
        native_min_value=5,
        native_step=5,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        value_fn=lambda data: math.floor(data[mp.AR_STABLE_TIME_1].total_seconds()),
        set_value_fn=lambda device, value: device.set(mp.AR_STABLE_TIME_1, value),
    ),
    MatisNumberEntityDescription(
        key=str(mp.AR_WAIT_TIME_2),
        native_max_value=3599,
        native_min_value=5,
        native_step=5,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        value_fn=lambda data: math.floor(data[mp.AR_WAIT_TIME_2].total_seconds()),
        set_value_fn=lambda device, value: device.set(mp.AR_WAIT_TIME_2, value),
    ),
    MatisNumberEntityDescription(
        key=str(mp.AR_STABLE_TIME_2),
        native_max_value=3599,
        native_min_value=5,
        native_step=5,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        value_fn=lambda data: math.floor(data[mp.AR_STABLE_TIME_2].total_seconds()),
        set_value_fn=lambda device, value: device.set(mp.AR_STABLE_TIME_2, value),
    ),
    MatisNumberEntityDescription(
        key=str(mp.AR_WAIT_TIME_3),
        native_max_value=3599,
        native_min_value=5,
        native_step=5,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        value_fn=lambda data: math.floor(data[mp.AR_WAIT_TIME_3].total_seconds()),
        set_value_fn=lambda device, value: device.set(mp.AR_WAIT_TIME_3, value),
    ),
    MatisNumberEntityDescription(
        key=str(mp.AR_STABLE_TIME_3),
        native_max_value=3599,
        native_min_value=5,
        native_step=5,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        value_fn=lambda data: math.floor(data[mp.AR_STABLE_TIME_3].total_seconds()),
        set_value_fn=lambda device, value: device.set(mp.AR_STABLE_TIME_3, value),
    ),
    MatisNumberEntityDescription(
        key=str(mp.AR_WAIT_TIME_4),
        native_max_value=3599,
        native_min_value=5,
        native_step=5,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        value_fn=lambda data: math.floor(data[mp.AR_WAIT_TIME_4].total_seconds()),
        set_value_fn=lambda device, value: device.set(mp.AR_WAIT_TIME_4, value),
    ),
    MatisNumberEntityDescription(
        key=str(mp.AR_STABLE_TIME_4),
        native_max_value=3599,
        native_min_value=5,
        native_step=5,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        value_fn=lambda data: math.floor(data[mp.AR_STABLE_TIME_4].total_seconds()),
        set_value_fn=lambda device, value: device.set(mp.AR_STABLE_TIME_4, value),
    ),
    MatisNumberEntityDescription(
        key=str(mp.AR_WAIT_TIME_5),
        native_max_value=3599,
        native_min_value=5,
        native_step=5,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        value_fn=lambda data: math.floor(data[mp.AR_WAIT_TIME_5].total_seconds()),
        set_value_fn=lambda device, value: device.set(mp.AR_WAIT_TIME_5, value),
    ),
    MatisNumberEntityDescription(
        key=str(mp.AR_STABLE_TIME_5),
        native_max_value=3599,
        native_min_value=5,
        native_step=5,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        value_fn=lambda data: math.floor(data[mp.AR_STABLE_TIME_5].total_seconds()),
        set_value_fn=lambda device, value: device.set(mp.AR_STABLE_TIME_5, value),
    ),
    MatisNumberEntityDescription(
        key=str(mp.AR_WAIT_TIME_6),
        native_max_value=3599,
        native_min_value=5,
        native_step=5,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        value_fn=lambda data: math.floor(data[mp.AR_WAIT_TIME_6].total_seconds()),
        set_value_fn=lambda device, value: device.set(mp.AR_WAIT_TIME_6, value),
    ),
    MatisNumberEntityDescription(
        key=str(mp.AR_STABLE_TIME_6),
        native_max_value=3599,
        native_min_value=5,
        native_step=5,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        value_fn=lambda data: math.floor(data[mp.AR_STABLE_TIME_6].total_seconds()),
        set_value_fn=lambda device, value: device.set(mp.AR_STABLE_TIME_6, value),
    ),
    MatisNumberEntityDescription(
        key=str(mp.AR_WAIT_TIME_7),
        native_max_value=3599,
        native_min_value=5,
        native_step=5,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        value_fn=lambda data: math.floor(data[mp.AR_WAIT_TIME_7].total_seconds()),
        set_value_fn=lambda device, value: device.set(mp.AR_WAIT_TIME_7, value),
    ),
    MatisNumberEntityDescription(
        key=str(mp.AR_STABLE_TIME_7),
        native_max_value=3599,
        native_min_value=5,
        native_step=5,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        value_fn=lambda data: math.floor(data[mp.AR_STABLE_TIME_7].total_seconds()),
        set_value_fn=lambda device, value: device.set(mp.AR_STABLE_TIME_7, value),
    ),
    MatisNumberEntityDescription(
        key=str(mp.AR_WAIT_TIME_8),
        native_max_value=3599,
        native_min_value=5,
        native_step=5,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        value_fn=lambda data: math.floor(data[mp.AR_WAIT_TIME_8].total_seconds()),
        set_value_fn=lambda device, value: device.set(mp.AR_WAIT_TIME_8, value),
    ),
    MatisNumberEntityDescription(
        key=str(mp.AR_STABLE_TIME_8),
        native_max_value=3599,
        native_min_value=5,
        native_step=5,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        value_fn=lambda data: math.floor(data[mp.AR_STABLE_TIME_8].total_seconds()),
        set_value_fn=lambda device, value: device.set(mp.AR_STABLE_TIME_8, value),
    ),
    MatisNumberEntityDescription(
        key=str(mp.AR_WAIT_TIME_9),
        native_max_value=3599,
        native_min_value=5,
        native_step=5,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        value_fn=lambda data: math.floor(data[mp.AR_WAIT_TIME_9].total_seconds()),
        set_value_fn=lambda device, value: device.set(mp.AR_WAIT_TIME_9, value),
    ),
    MatisNumberEntityDescription(
        key=str(mp.AR_STABLE_TIME_9),
        native_max_value=3599,
        native_min_value=5,
        native_step=5,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        value_fn=lambda data: math.floor(data[mp.AR_STABLE_TIME_9].total_seconds()),
        set_value_fn=lambda device, value: device.set(mp.AR_STABLE_TIME_9, value),
    ),
    MatisNumberEntityDescription(
        key=str(mp.AR_WAIT_TIME_10),
        native_max_value=3599,
        native_min_value=5,
        native_step=5,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        value_fn=lambda data: math.floor(data[mp.AR_WAIT_TIME_10].total_seconds()),
        set_value_fn=lambda device, value: device.set(mp.AR_WAIT_TIME_10, value),
    ),
    MatisNumberEntityDescription(
        key=str(mp.AR_STABLE_TIME_10),
        native_max_value=3599,
        native_min_value=5,
        native_step=5,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        value_fn=lambda data: math.floor(data[mp.AR_STABLE_TIME_10].total_seconds()),
        set_value_fn=lambda device, value: device.set(mp.AR_STABLE_TIME_10, value),
    ),
)


class MatisNumberEntity(MatisEntity, NumberEntity):  # type: ignore[override] # pylint: disable=abstract-method
    """Matis number."""

    entity_description: MatisNumberEntityDescription

    def __init__(
        self,
        description: MatisNumberEntityDescription,
        coordinator: MatisDataUpdateCoordinator,
    ) -> None:
        """Initialize the Matis number entity."""
        super().__init__(coordinator, description)
        self.entity_description = description  # type: ignore[override]

    async def _set_value_internal(self, value: float) -> bool:
        if self.entity_description.set_value_fn is None:
            raise NotImplementedError
        return await self.entity_description.set_value_fn(
            self.coordinator.api, math.floor(value)
        )

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        update_needed = await self._set_value_internal(value)
        if update_needed:
            await self.coordinator.async_request_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle update data from the coordinator."""
        LOGGER.debug(
            "Handle update for number %s",
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
    """Set up the numbers."""
    entities: list[NumberEntity] = []
    coordinator: MatisDataUpdateCoordinator = entry.runtime_data
    hardware_id = coordinator.data[mp.HARDWARE_ID]
    if hardware_id == MatisHardwareId.MT53RA_SX:
        entities.extend(
            [
                MatisNumberEntity(description, coordinator)
                for description in MT53RA_SX_NUMBER_ENTITIES
            ]
        )
    async_add_entities(entities)
