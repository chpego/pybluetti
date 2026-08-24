"""
Async Python client for the BLUETTI cloud API.

Extracted from
https://github.com/bluetti-official/bluetti-home-assistant's
custom_components/bluetti/api/, the same way
https://github.com/pyenphase/pyenphase backs the enphase_envoy Home Assistant
integration.

This is step 1 of the extraction: a mechanical move, decoupled from Home
Assistant, with the transport unchanged (still the blocking
`websocket-client` library run on a dedicated thread). Replacing it with
`aiohttp`'s native async websocket, and wiring bluetti-home-assistant to
depend on this package, are separate follow-ups.
"""

from .client import Bluetti
from .const import Method
from .exceptions import ApplicationRuntimeException
from .models import UserProduct
from .product_client import ProductClient
from .unify_response import UnifyResponse
from .websocket import StompClient, StompListener

__version__ = "0.1.0"

__all__ = [
    "ApplicationRuntimeException",
    "Bluetti",
    "Method",
    "ProductClient",
    "StompClient",
    "StompListener",
    "UnifyResponse",
    "UserProduct",
]
