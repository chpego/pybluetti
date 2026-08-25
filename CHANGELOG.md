# 0.1.1

- Adopted `mypy --strict` across the whole package (wired into CI via `scripts/typecheck`), fulfilling the "strict-typing" requirement of Home Assistant's Platinum integration quality scale. Along the way, fixed a real type-unsoundness bug: `Bluetti` was declared `Generic[T]` at the class level but never actually parametrized per instance - `_request()` now returns `UnifyResponse[Any] | str`, with `ProductClient`'s public methods restoring a precise type via `typing.cast` at the boundary where `pydantic.TypeAdapter` already validated it at runtime.
- Moved to the `bluetti-community` GitHub organization (was `pybluetti`); no change to the PyPI package name or install command.

# 0.1.0

- Replaced `StompClient`'s blocking `websocket-client` transport (a dedicated daemon thread plus a second dedicated heartbeat thread) with `aiohttp`'s native async websocket client (`ClientSession.ws_connect`). `connect()`/`disconnect()`/`reconnect()` are now coroutines; the receive loop and heartbeat run as `asyncio.Task`s instead of threads. `StompListener` is folded into `StompClient` (no more callback registration to justify a separate object). STOMP protocol framing (`stomper`) and all frame-handling logic/log messages are unchanged. `websocket-client` dropped from dependencies.
- Migrated the BLUETTI cloud API client from `bluetti-home-assistant`'s `custom_components/bluetti/api/` (plus `model/product.py` and `application_exception.py`): `Bluetti`/`ProductClient` (HTTP), `StompClient`/`StompListener` (websocket push updates), `UserProduct`, `UnifyResponse`, `ApplicationRuntimeException`. Decoupled from Home Assistant - server URLs and an `on_auth_expired` callback are now plain constructor arguments instead of a `hass` object. The websocket transport itself (`websocket-client` on a dedicated thread) is unchanged in this step.
- Initial repository scaffold: packaging (`pyproject.toml`, `hatchling`), test/lint scripts, CI, MIT license.
