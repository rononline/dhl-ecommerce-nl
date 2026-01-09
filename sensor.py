from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import homeassistant.util.dt as dt_util
from datetime import datetime

from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    # Maak een sensor aan voor dit account
    async_add_entities([DHLParcelSensor(coordinator, entry.title)], True)

class DHLParcelSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, email):
        super().__init__(coordinator)
        self._email = email
        self._attr_name = f"DHL Packages {email}"
        self._attr_unique_id = f"dhl_{email}_packages"
        self._attr_icon = "mdi:package-variant-closed" # Of phu:dhl als je custom packs hebt
        self._attr_unit_of_measurement = "packages"

    @property
    def native_value(self):
        """Aantal niet-geleverde pakketten."""
        parcels = self.coordinator.data or []
        
        active = []
        for p in parcels:
            # Check 1: Is de hoofdcategorie 'DELIVERED'? Dan negeren.
            if p.get('category') == 'DELIVERED':
                continue
            
            # Check 2: Bevat de status tekst 'DELIVERED'? Dan negeren (vangnet).
            status = p.get('status', '')
            if 'DELIVERED' in status:
                continue
                
            # Als hij hier komt, is het een actief pakket
            active.append(p)

        return len(active)

    @property
    def extra_state_attributes(self):
        """De attributen (expect_now, window, etc)."""
        parcels = self.coordinator.data or []
        # Filter: alles wat niet delivered is
        active_parcels = [p for p in parcels if p.get('category') != 'DELIVERED']

        attrs = {
            "parcels_json": parcels, 
            "expect_now": "notexpecting",
            "deliver_window": "Unknown"
        }

        if not active_parcels:
            return attrs

        package = active_parcels[0]
        time_info = package.get("receivingTimeIndication")

        if time_info and time_info.get("start") and time_info.get("end"):
            try:
                start_dt = datetime.fromisoformat(time_info['start'].replace("Z", "+00:00"))
                end_dt = datetime.fromisoformat(time_info['end'].replace("Z", "+00:00"))
                now = dt_util.now() # Tijdzone bewust

                if now > start_dt:
                    if now < end_dt:
                        attrs["expect_now"] = "expecting"
                    else:
                        attrs["expect_now"] = "overdue"
                else:
                    attrs["expect_now"] = "notexpecting"

                local_start = dt_util.as_local(start_dt)
                local_end = dt_util.as_local(end_dt)
                attrs["deliver_window"] = f"{local_start.strftime('%H:%M')} - {local_end.strftime('%H:%M')}"

            except Exception as e:
                attrs["deliver_window"] = "Error parsing date"
        
        return attrs
