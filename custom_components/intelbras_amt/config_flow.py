"""Config flow for Intelbras AMT integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .client import AMTClient, AMTClientError
from .const import (
    CONF_PASSWORD_A,
    CONF_PASSWORD_B,
    CONF_PASSWORD_C,
    CONF_PASSWORD_D,
    CONF_SCAN_INTERVAL,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
        vol.Required(CONF_PASSWORD): str,
    }
)

STEP_PARTITIONS_DATA_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_PASSWORD_A): str,
        vol.Optional(CONF_PASSWORD_B): str,
        vol.Optional(CONF_PASSWORD_C): str,
        vol.Optional(CONF_PASSWORD_D): str,
    }
)


class AMTConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Intelbras AMT."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._data: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Test connection
            client = AMTClient(
                host=user_input[CONF_HOST],
                port=user_input[CONF_PORT],
                password=user_input[CONF_PASSWORD],
            )

            try:
                await client.connect()
                status = await client.get_status()
                await client.disconnect()

                # Store data for next step
                self._data = user_input
                self._data["model_name"] = status.get("model_name", "AMT")

                # Check if already configured
                await self.async_set_unique_id(
                    f"amt_{user_input[CONF_HOST]}_{user_input[CONF_PORT]}"
                )
                self._abort_if_unique_id_configured()

                # Proceed to partition passwords step
                return await self.async_step_partitions()

            except AMTClientError as err:
                _LOGGER.error("Connection failed: %s", err)
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected error")
                errors["base"] = "unknown"
            finally:
                await client.disconnect()

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_partitions(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the partition passwords step."""
        if user_input is not None:
            # Merge partition passwords into data
            self._data.update(user_input)

            # Add default scan interval
            self._data[CONF_SCAN_INTERVAL] = DEFAULT_SCAN_INTERVAL

            return self.async_create_entry(
                title=f"{self._data.get('model_name', 'AMT')} ({self._data[CONF_HOST]})",
                data=self._data,
            )

        return self.async_show_form(
            step_id="partitions",
            data_schema=STEP_PARTITIONS_DATA_SCHEMA,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Get the options flow for this handler."""
        return AMTOptionsFlow(config_entry)


class AMTOptionsFlow(OptionsFlow):
    """Handle options flow for Intelbras AMT."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SCAN_INTERVAL,
                        default=self._config_entry.options.get(
                            CONF_SCAN_INTERVAL,
                            self._config_entry.data.get(
                                CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                            ),
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=60)),
                    vol.Optional(
                        CONF_PASSWORD_A,
                        default=self._config_entry.data.get(CONF_PASSWORD_A, ""),
                    ): str,
                    vol.Optional(
                        CONF_PASSWORD_B,
                        default=self._config_entry.data.get(CONF_PASSWORD_B, ""),
                    ): str,
                    vol.Optional(
                        CONF_PASSWORD_C,
                        default=self._config_entry.data.get(CONF_PASSWORD_C, ""),
                    ): str,
                    vol.Optional(
                        CONF_PASSWORD_D,
                        default=self._config_entry.data.get(CONF_PASSWORD_D, ""),
                    ): str,
                }
            ),
        )
