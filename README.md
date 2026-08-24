# pybluetti

Async Python client for the BLUETTI cloud API - device discovery, state, and control.

## Status: client code migrated, not yet wired up or published

This repository is the extraction target for the API client code that used to
live in
[`bluetti-home-assistant`](https://github.com/bluetti-official/bluetti-home-assistant)'s
`custom_components/bluetti/api/`, following the same pattern
[`pyenphase`](https://github.com/pyenphase/pyenphase) uses for the `enphase_envoy`
Home Assistant integration: a standalone, independently testable and
versionable library, decoupled from Home Assistant's own release cycle.

The extraction is happening in three steps:

1. **Done.** Move the client code here mechanically, decoupled from `hass`
   (server URLs and an `on_auth_expired` callback are passed in as plain
   constructor arguments instead - see `src/pybluetti/`). The websocket
   transport is unchanged for now.
2. *Not started.* Replace the blocking `websocket-client` transport
   (`src/pybluetti/websocket.py`, currently run on a dedicated thread to keep
   it out of Home Assistant's event loop) with `aiohttp`'s native async
   websocket support.
3. *Not started.* Publish to PyPI, and switch `bluetti-home-assistant`'s
   `manifest.json`/imports to depend on this package instead of its own
   in-tree copy.

## Why extract it

- **Independent testing and versioning**, not tied to Home Assistant's release cadence.
- **A step toward Home Assistant core inclusion** - core integrations are expected to depend on
  an external library for the actual device/API communication, not embed raw HTTP/websocket
  calls directly in the integration.
- **A natural point to fix a known gap**: the current embedded client uses the blocking
  `websocket-client` library (see `custom_components/bluetti/api/websocket.py`, which runs it on
  a dedicated thread to keep it out of Home Assistant's event loop). Migrating to `aiohttp`'s
  native async websocket support removes that workaround entirely.

## Development

```bash
scripts/setup   # install runtime + test dependencies
scripts/test    # run the test suite (100% line coverage enforced)
scripts/lint    # run ruff, auto-fixing what it safely can
```

## License

MIT - see [LICENSE](LICENSE).
