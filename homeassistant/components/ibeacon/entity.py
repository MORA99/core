"""Support for iBeacon device sensors."""
from __future__ import annotations

from abc import abstractmethod

from ibeacon_ble import iBeaconAdvertisement

from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo, Entity

from .const import ATTR_MAJOR, ATTR_MINOR, ATTR_SOURCE, ATTR_UUID, DOMAIN
from .coordinator import IBeaconCoordinator, signal_seen, signal_unavailable


class IBeaconEntity(Entity):
    """An iBeacon entity."""

    _attr_should_poll = False
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: IBeaconCoordinator,
        identifier: str,
        device_unique_id: str,
        parsed: iBeaconAdvertisement,
    ) -> None:
        """Initialize an iBeacon sensor entity."""
        self._device_unique_id = device_unique_id
        self._coordinator = coordinator
        self._parsed = parsed
        self._attr_device_info = DeviceInfo(
            name=identifier,
            identifiers={(DOMAIN, device_unique_id)},
        )

    @property
    def extra_state_attributes(
        self,
    ) -> dict[str, str | int]:
        """Return the device state attributes."""
        parsed = self._parsed
        return {
            ATTR_UUID: str(parsed.uuid),
            ATTR_MAJOR: parsed.major,
            ATTR_MINOR: parsed.minor,
            ATTR_SOURCE: parsed.source,
        }

    @abstractmethod
    @callback
    def _async_seen(
        self,
        parsed: iBeaconAdvertisement,
    ) -> None:
        """Update state."""

    @abstractmethod
    @callback
    def _async_unavailable(self) -> None:
        """Set unavailable."""

    async def async_added_to_hass(self) -> None:
        """Register state update callbacks."""
        await super().async_added_to_hass()
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                signal_seen(self._device_unique_id),
                self._async_seen,
            )
        )
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                signal_unavailable(self._device_unique_id),
                self._async_unavailable,
            )
        )
