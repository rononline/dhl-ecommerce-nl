from datetime import timedelta
import logging

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .api import DHLApi

_LOGGER = logging.getLogger(__name__)

class DHLCoordinator(DataUpdateCoordinator):
    """Class to manage fetching DHL data."""

    def __init__(self, hass, api: DHLApi):
        self.api = api
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=30), # Elke 30 min update
        )

    async def _async_update_data(self):
        """Fetch data from API."""
        try:
            return await self.api.get_parcels()
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")
