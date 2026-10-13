"""Capteur pour afficher si aujourd'hui est un jour férié."""
import logging
from datetime import date
from homeassistant.components.sensor import SensorEntity
from .const import (
    DOMAIN, SENSOR_NAME, SENSOR_UNIQUE_ID,
    ATTR_HOLIDAY_NAME, ATTR_DATE, ATTR_NEXT_HOLIDAY, ATTR_DAYS_UNTIL,
    ATTR_PROCHAIN_PONT_POTENTIEL, CONF_WEEKEND_DAYS, DEFAULT_WEEKEND_DAYS,
    WEEKEND_DAY_INDEXES, get_holidays, get_next_potential_bridge,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    weekend_days = entry.options.get(
        CONF_WEEKEND_DAYS,
        entry.data.get(CONF_WEEKEND_DAYS, DEFAULT_WEEKEND_DAYS),
    )
    weekend_day_indexes = {
        WEEKEND_DAY_INDEXES[day]
        for day in weekend_days
        if day in WEEKEND_DAY_INDEXES
    }
    async_add_entities([JourFerieSensor(weekend_day_indexes)])

class JourFerieSensor(SensorEntity):
    def __init__(self, weekend_days: set[int]):
        self._attr_name = SENSOR_NAME
        self._attr_unique_id = SENSOR_UNIQUE_ID
        self._attr_icon = "mdi:calendar-star"
        self._state = None
        self._attributes = {}
        self._weekend_days = weekend_days
        self._attr_device_info = {
            "identifiers": {(DOMAIN, "jourferier")},
            "name": "Jour Férié",
            "manufacturer": "xav59213",
            "model": "Capteur jours fériés dynamique",
            "sw_version": "1.0.6",
            "configuration_url": "https://github.com/xav59213/xav59213-jour-ferie",
        }

    def update(self):
        today = date.today()
        holidays = get_holidays(today.year)
        today_holiday = holidays.get(today)
        self._state = today_holiday if today_holiday else "Aucun"

        # Inclure aussi l'année suivante pour calcul anticipé
        all_holidays = {**holidays, **get_holidays(today.year + 1)}
        next_holiday = None
        days_until = None
        for holiday_date in sorted(all_holidays):
            if holiday_date > today:
                next_holiday = all_holidays[holiday_date]
                days_until = (holiday_date - today).days
                break

        next_potential_bridge = get_next_potential_bridge(today, self._weekend_days)

        self._attributes = {
            ATTR_HOLIDAY_NAME: self._state,
            ATTR_DATE: today.strftime("%d:%m"),
            ATTR_NEXT_HOLIDAY: next_holiday,
            ATTR_DAYS_UNTIL: days_until,
            ATTR_PROCHAIN_PONT_POTENTIEL: (
                next_potential_bridge.strftime("%d:%m")
                if next_potential_bridge
                else "Aucun"
            ),
        }

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attributes
