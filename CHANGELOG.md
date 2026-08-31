# 0.2.1rc1 (pre-release)

- Fixed `_run()` leaving the abandoned connection open on every path except a token-expiry (msgCode 805): an `ApplicationRuntimeException`, a plain ERROR/CLOSE message, or an unexpected crash all left `close()` uncalled on the old connection. 0.2.0's heartbeat-task cancellation in `connect()` was only a partial fix - the still-open connection let a concurrently-running heartbeat send slip past its own is-it-closed check and fail against the transport before aiohttp itself noticed the remote side had already closed, reported as "Failed to send heartbeat: Cannot write to closing transport" repeating on every reconnect cycle in production (real-world confirmation: bluetti-official/bluetti-home-assistant#145). `_run()` now closes the connection itself as soon as it decides to abandon it, closing that race instead of just narrowing it.

# 0.2.0

- **Breaking**: `StompClient.__init__`'s `handler`, `on_auth_expired`, and the new `on_error` are now keyword-only (`session`/`url`/`access_token` stay positional). Update any call passing `handler` positionally to `handler=...`.
- Added `StompClient(on_error=...)`, invoked for any ERROR frame the cloud sends back other than a token-expiry (msgCode 805) - previously invisible to a caller beyond a bare `.exception()` log line inside `_run()`'s own retry loop.
- Fixed `StompClient` leaking the previous connection's heartbeat task into every reconnect that follows a dropped or rejected connection - `connect()` now cancels it first, instead of the task quietly failing its next send against the closing transport.
- `StompClient` no longer re-logs a full traceback on every retry of a persistently repeated `ApplicationRuntimeException` - only the first occurrence and any occurrence with a different message log at full severity; repeats log at debug.

# 0.1.1

- Adopted `mypy --strict` across the whole package (wired into CI via `scripts/typecheck`), fulfilling the "strict-typing" requirement of Home Assistant's Platinum integration quality scale. Along the way, fixed a real type-unsoundness bug: `Bluetti` was declared `Generic[T]` at the class level but never actually parametrized per instance - `_request()` now returns `UnifyResponse[Any] | str`, with `ProductClient`'s public methods restoring a precise type via `typing.cast` at the boundary where `pydantic.TypeAdapter` already validated it at runtime.
- Moved to the `bluetti-community` GitHub organization (was `pybluetti`); no change to the PyPI package name or install command.

# 0.1.0

- Replaced `StompClient`'s blocking `websocket-client` transport (a dedicated daemon thread plus a second dedicated heartbeat thread) with `aiohttp`'s native async websocket client (`ClientSession.ws_connect`). `connect()`/`disconnect()`/`reconnect()` are now coroutines; the receive loop and heartbeat run as `asyncio.Task`s instead of threads. `StompListener` is folded into `StompClient` (no more callback registration to justify a separate object). STOMP protocol framing (`stomper`) and all frame-handling logic/log messages are unchanged. `websocket-client` dropped from dependencies.
- Migrated the BLUETTI cloud API client from `bluetti-home-assistant`'s `custom_components/bluetti/api/` (plus `model/product.py` and `application_exception.py`): `Bluetti`/`ProductClient` (HTTP), `StompClient`/`StompListener` (websocket push updates), `UserProduct`, `UnifyResponse`, `ApplicationRuntimeException`. Decoupled from Home Assistant - server URLs and an `on_auth_expired` callback are now plain constructor arguments instead of a `hass` object. The websocket transport itself (`websocket-client` on a dedicated thread) is unchanged in this step.
- Initial repository scaffold: packaging (`pyproject.toml`, `hatchling`), test/lint scripts, CI, MIT license.
