# pybluetti

Async Python client for the BLUETTI cloud API - device discovery, state, and control.

## Status: fully async, not yet wired up or published

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
   constructor arguments instead - see `src/pybluetti/`).
2. **Done.** Replace the blocking `websocket-client` transport (previously
   run on a dedicated thread to keep it out of Home Assistant's event loop)
   with `aiohttp`'s native async websocket client - `src/pybluetti/websocket.py`
   has no threads left. STOMP protocol framing (`stomper`) is unchanged.
3. *Not started.* Publish to PyPI, and switch `bluetti-home-assistant`'s
   `manifest.json`/imports to depend on this package instead of its own
   in-tree copy.

## Why extract it

- **Independent testing and versioning**, not tied to Home Assistant's release cadence.
- **A step toward Home Assistant core inclusion** - core integrations are expected to depend on
  an external library for the actual device/API communication, not embed raw HTTP/websocket
  calls directly in the integration.
- **Fixed a known gap along the way**: the embedded client used to run the blocking
  `websocket-client` library on a dedicated thread to keep it out of Home Assistant's event
  loop. `pybluetti` is fully async instead, matching `bluetti-home-assistant`'s own
  `quality_scale.yaml` `async-dependency` goal once step 3 wires it up.

## Development

```bash
scripts/setup   # install runtime + test dependencies
scripts/test    # run the test suite (100% line coverage enforced)
scripts/lint    # run ruff, auto-fixing what it safely can
```

## License

MIT - see [LICENSE](LICENSE).
