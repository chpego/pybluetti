"""Client for the BLUETTI product/device endpoints."""

import logging

from .client import Bluetti
from .const import Method
from .models import UserProduct
from .unify_response import UnifyResponse


class ProductClient(Bluetti):
    """Class describing for the BLUETTI products."""

    __LOGGER__ = None
    """The api client logger."""

    @property
    def logger(self) -> logging.Logger:
        """Get the api client logger."""
        if self.__LOGGER__ is None:
            self.__LOGGER__ = logging.getLogger(__name__ + "." + __class__.__name__)
        return self.__LOGGER__

    async def get_user_products(self) -> UnifyResponse[list[UserProduct]]:
        """Get the devices/power stations bound to the account."""
        return await self._request(
            list[UserProduct],
            Method.GET,
            "/api/bluiotdata/ha/v1/devices",
        )

    async def get_device_status(self, sns: str | None = None) -> UnifyResponse[list[UserProduct]]:
        """Poll device state."""
        return await self._request(
            list[UserProduct],
            Method.GET,
            "/api/bluiotdata/ha/v1/deviceStates",
            params={"sns": sns},
        )

    async def control_device(self, payload: dict | None = None) -> UnifyResponse[dict] | str:
        """Send a control command to a device."""
        return await self._request(
            dict,
            method=Method.POST,
            path="/api/bluiotdata/ha/v1/fulfillment",
            body=payload,
        )

    async def bind_devices(self, payload: dict | None = None) -> UnifyResponse[dict] | str:
        """Bind devices to the account."""
        return await self._request(
            dict,
            method=Method.POST,
            path="/api/bluiotdata/ha/v1/bindDevices",
            body=payload,
        )
