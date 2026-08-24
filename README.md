# pybluetti

Async Python client for the BLUETTI cloud API - device discovery, state, and control.

## Status: scaffold, not yet functional

This repository is the extraction target for the API client code currently
embedded in
[`bluetti-home-assistant`](https://github.com/bluetti-official/bluetti-home-assistant)'s
[`custom_components/bluetti/api/`](https://github.com/bluetti-official/bluetti-home-assistant/tree/main/custom_components/bluetti/api),
following the same pattern
[`pyenphase`](https://github.com/pyenphase/pyenphase) uses for the `enphase_envoy`
Home Assistant integration: a standalone, independently testable and
versionable library, decoupled from Home Assistant's own release cycle.

No client code has been migrated yet - this repo currently only has packaging,
CI, and test scaffolding in place. Once the migration lands, `pybluetti` will
be a normal PyPI dependency of `bluetti-home-assistant` instead of code living
inside that repo.

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
