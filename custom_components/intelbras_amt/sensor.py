"""Sensors for Intelbras AMT integration."""

from __future__ import annotations

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, PERCENTAGE, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DATA_BATTERY_LEVEL,
    DATA_CONNECTED,
    DATA_FIRMWARE,
    DATA_MODEL_NAME,
    DOMAIN,
    ENTITY_PREFIX,
)
from .coordinator import AMTCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors from a config entry."""
    coordinator: AMTCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SensorEntity] = [
        AMTBatteryLevelSensor(coordinator, entry),
        AMTModelSensor(coordinator, entry),
        AMTFirmwareSensor(coordinator, entry),
    ]

    async_add_entities(entities)


class AMTSensorBase(CoordinatorEntity[AMTCoordinator], SensorEntity):
    """Base class for AMT sensors."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: AMTCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        model_name = "AMT"
        if self.coordinator.data:
            model_name = self.coordinator.data.get(DATA_MODEL_NAME, "AMT")

        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=f"{ENTITY_PREFIX.upper()} {self._entry.data[CONF_HOST]}",
            manufacturer="Intelbras",
            model=model_name,
        )

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        if not self.coordinator.data:
            return False
        return self.coordinator.data.get(DATA_CONNECTED, False)


class AMTBatteryLevelSensor(AMTSensorBase):
    """Battery level sensor."""

    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_name = "Nível da Bateria"

    def __init__(
        self,
        coordinator: AMTCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the battery sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_battery_level"

    @property
    def native_value(self) -> int | None:
        """Return the battery level."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get(DATA_BATTERY_LEVEL)


class AMTModelSensor(AMTSensorBase):
    """Model sensor."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_name = "Modelo"

    def __init__(
        self,
        coordinator: AMTCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the model sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_model"

    @property
    def native_value(self) -> str | None:
        """Return the model name."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get(DATA_MODEL_NAME)


class AMTFirmwareSensor(AMTSensorBase):
    """Firmware version sensor."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_name = "Firmware"

    def __init__(
        self,
        coordinator: AMTCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the firmware sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_firmware"

    @property
    def native_value(self) -> str | None:
        """Return the firmware version."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get(DATA_FIRMWARE)
