# Unreleased

- Migrated the BLUETTI cloud API client from `bluetti-home-assistant`'s `custom_components/bluetti/api/` (plus `model/product.py` and `application_exception.py`): `Bluetti`/`ProductClient` (HTTP), `StompClient`/`StompListener` (websocket push updates), `UserProduct`, `UnifyResponse`, `ApplicationRuntimeException`. Decoupled from Home Assistant - server URLs and an `on_auth_expired` callback are now plain constructor arguments instead of a `hass` object. The websocket transport itself (`websocket-client` on a dedicated thread) is unchanged in this step.
- Initial repository scaffold: packaging (`pyproject.toml`, `hatchling`), test/lint scripts, CI, MIT license.
