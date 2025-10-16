"""Coordinator for the Matis integration."""

import datetime
import logging
from typing import Any, Dict

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from pymatis.device import MatisDevice
from pymatis.exceptions import MatisException
from pymatis.properties import MatisProperty

from .const import DEFAULT_NAME

LOGGER = logging.getLogger(__name__)

type MatisDeviceData = Dict[MatisProperty, Any]


class MatisDataUpdateCoordinator(DataUpdateCoordinator[MatisDeviceData]):
    """The Matismart data update coordinator."""

    api: MatisDevice

    def __init__(
        self,
        hass: HomeAssistant,
        api: MatisDevice,
        update_interval: int,
    ) -> None:
        """Initialize the Matis data coordinator."""
        super().__init__(
            hass,
            LOGGER,
            name=f"{DEFAULT_NAME} DataUpdateCoordinator",
            update_interval=datetime.timedelta(seconds=update_interval),
        )
        self.api = api

    async def _async_update_data(self) -> MatisDeviceData:
        """Fetch state from API."""
        try:
            data = await self.api.fetch()
            return data
        except MatisException as err:
            msg = "Error during state cache update"
            raise UpdateFailed(msg) from err
