"""Buttons for Intelbras AMT integration."""

from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DATA_CONNECTED,
    DATA_MODEL_NAME,
    DOMAIN,
    ENTITY_PREFIX,
    MAX_PARTITIONS,
    MAX_PGMS,
    PARTITION_NAMES,
)
from .coordinator import AMTCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up buttons from a config entry."""
    coordinator: AMTCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[ButtonEntity] = []

    # Main arm/disarm/stay buttons
    entities.append(AMTArmButton(coordinator, entry))
    entities.append(AMTDisarmButton(coordinator, entry))
    entities.append(AMTStayButton(coordinator, entry))

    # Partition arm/disarm buttons
    for partition_idx in range(MAX_PARTITIONS):
        partition_name = PARTITION_NAMES[partition_idx]
        entities.append(AMTArmPartitionButton(coordinator, entry, partition_name))
        entities.append(AMTDisarmPartitionButton(coordinator, entry, partition_name))

    # PGM activation buttons
    for pgm_num in range(1, MAX_PGMS + 1):
        entities.append(AMTPGMActivateButton(coordinator, entry, pgm_num))
        entities.append(AMTPGMDeactivateButton(coordinator, entry, pgm_num))

    # Bypass open zones button
    entities.append(AMTBypassOpenZonesButton(coordinator, entry))

    async_add_entities(entities)


class AMTButtonBase(CoordinatorEntity[AMTCoordinator], ButtonEntity):
    """Base class for AMT buttons."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: AMTCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the button."""
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


class AMTArmButton(AMTButtonBase):
    """Arm button."""

    _attr_name = "Armar"
    _attr_icon = "mdi:shield-lock"

    def __init__(
        self,
        coordinator: AMTCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the arm button."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_arm"

    async def async_press(self) -> None:
        """Handle button press."""
        await self.coordinator.async_arm()


class AMTDisarmButton(AMTButtonBase):
    """Disarm button."""

    _attr_name = "Desarmar"
    _attr_icon = "mdi:shield-off"

    def __init__(
        self,
        coordinator: AMTCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the disarm button."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_disarm"

    async def async_press(self) -> None:
        """Handle button press."""
        await self.coordinator.async_disarm()


class AMTStayButton(AMTButtonBase):
    """Stay mode button."""

    _attr_name = "Armar Stay"
    _attr_icon = "mdi:shield-home"

    def __init__(
        self,
        coordinator: AMTCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the stay button."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_stay"

    async def async_press(self) -> None:
        """Handle button press."""
        await self.coordinator.async_arm_stay()


class AMTArmPartitionButton(AMTButtonBase):
    """Arm partition button."""

    _attr_icon = "mdi:shield-lock-outline"

    def __init__(
        self,
        coordinator: AMTCoordinator,
        entry: ConfigEntry,
        partition_name: str,
    ) -> None:
        """Initialize the arm partition button."""
        super().__init__(coordinator, entry)
        self._partition_name = partition_name
        self._attr_unique_id = f"{entry.entry_id}_arm_partition_{partition_name.lower()}"
        self._attr_name = f"Armar Partição {partition_name}"

    async def async_press(self) -> None:
        """Handle button press."""
        await self.coordinator.async_arm_partition(self._partition_name)


class AMTDisarmPartitionButton(AMTButtonBase):
    """Disarm partition button."""

    _attr_icon = "mdi:shield-off-outline"

    def __init__(
        self,
        coordinator: AMTCoordinator,
        entry: ConfigEntry,
        partition_name: str,
    ) -> None:
        """Initialize the disarm partition button."""
        super().__init__(coordinator, entry)
        self._partition_name = partition_name
        self._attr_unique_id = f"{entry.entry_id}_disarm_partition_{partition_name.lower()}"
        self._attr_name = f"Desarmar Partição {partition_name}"

    async def async_press(self) -> None:
        """Handle button press."""
        await self.coordinator.async_disarm_partition(self._partition_name)


class AMTPGMActivateButton(AMTButtonBase):
    """PGM activate button."""

    _attr_icon = "mdi:electric-switch"

    def __init__(
        self,
        coordinator: AMTCoordinator,
        entry: ConfigEntry,
        pgm_num: int,
    ) -> None:
        """Initialize the PGM activate button."""
        super().__init__(coordinator, entry)
        self._pgm_num = pgm_num
        self._attr_unique_id = f"{entry.entry_id}_pgm_{pgm_num}_activate"
        self._attr_name = f"Ativar PGM {pgm_num}"

    async def async_press(self) -> None:
        """Handle button press."""
        await self.coordinator.async_activate_pgm(self._pgm_num)


class AMTPGMDeactivateButton(AMTButtonBase):
    """PGM deactivate button."""

    _attr_icon = "mdi:electric-switch-closed"

    def __init__(
        self,
        coordinator: AMTCoordinator,
        entry: ConfigEntry,
        pgm_num: int,
    ) -> None:
        """Initialize the PGM deactivate button."""
        super().__init__(coordinator, entry)
        self._pgm_num = pgm_num
        self._attr_unique_id = f"{entry.entry_id}_pgm_{pgm_num}_deactivate"
        self._attr_name = f"Desativar PGM {pgm_num}"

    async def async_press(self) -> None:
        """Handle button press."""
        await self.coordinator.async_deactivate_pgm(self._pgm_num)


class AMTBypassOpenZonesButton(AMTButtonBase):
    """Bypass open zones button."""

    _attr_name = "Anular Zonas Abertas"
    _attr_icon = "mdi:shield-link-variant"

    def __init__(
        self,
        coordinator: AMTCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the bypass button."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_bypass_open_zones"

    async def async_press(self) -> None:
        """Handle button press."""
        await self.coordinator.async_bypass_open_zones()
