"""Flux de configuration pour Jour Férié."""
import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv

from .const import (
    CONF_WEEKEND_DAYS,
    DEFAULT_WEEKEND_DAYS,
    DOMAIN,
    WEEKEND_DAY_OPTIONS,
)

_LOGGER = logging.getLogger(__name__)


def _weekend_days_schema(default_weekend_days):
    """Retourne le schéma de sélection des jours de week-end."""
    return vol.Schema(
        {
            vol.Required(
                CONF_WEEKEND_DAYS,
                default=list(default_weekend_days),
            ): cv.multi_select(WEEKEND_DAY_OPTIONS),
        }
    )


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Gérer le flux de configuration."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Gérer l'étape utilisateur."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_only")

        if user_input is not None:
            return self.async_create_entry(title="Jour Férié", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=_weekend_days_schema(DEFAULT_WEEKEND_DAYS),
            errors={},
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Retourne le flux d'options de l'intégration."""
        return OptionsFlowHandler()


class OptionsFlowHandler(config_entries.OptionsFlowWithReload):
    """Gérer les options de Jour Férié."""

    async def async_step_init(self, user_input=None):
        """Gérer la sélection des jours de week-end."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        weekend_days = self.config_entry.options.get(
            CONF_WEEKEND_DAYS,
            self.config_entry.data.get(CONF_WEEKEND_DAYS, DEFAULT_WEEKEND_DAYS),
        )
        return self.async_show_form(
            step_id="init",
            data_schema=_weekend_days_schema(weekend_days),
            errors={},
        )
