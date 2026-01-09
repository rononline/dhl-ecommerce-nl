import aiohttp
import async_timeout
import logging

from .const import LOGIN_URL, PARCELS_URL

_LOGGER = logging.getLogger(__name__)

class DHLApi:
    def __init__(self, email, password, session: aiohttp.ClientSession):
        self._email = email
        self._password = password
        self._session = session
        self._token = None

    async def authenticate(self):
        """Login and retrieve session cookies/token."""
        payload = {"email": self._email, "password": self._password}
        try:
            async with async_timeout.timeout(10):
                resp = await self._session.post(LOGIN_URL, json=payload)
                resp.raise_for_status()
                # De sessie onthoudt nu de cookies automatisch
        except Exception as e:
            _LOGGER.error("Fout bij inloggen DHL: %s", e)
            raise

    async def get_parcels(self):
        """Fetch parcels."""
        await self.authenticate()
        
        try:
            async with async_timeout.timeout(10):
                headers = {"Content-Type": "application/json"}
                resp = await self._session.get(PARCELS_URL, headers=headers)
                resp.raise_for_status()
                data = await resp.json()
                return data.get("parcels", [])
        except Exception as e:
            _LOGGER.error("Fout bij ophalen pakketten: %s", e)
            raise
