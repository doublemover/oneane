# Unified artifacts

This folder consolidates machine-readable artifacts used throughout the repo:
- OpenAPI / AsyncAPI specifications
- firmware-derived HTTP route unions
- corrected JSON Schemas for HTTP models, Socket.IO events, and Socket.IO commands
- small indexes and manifests used by the Python GUI and the unified clients

If you are building a client or tooling, this directory is the best starting point for machine-consumable inputs.

## What to treat as authoritative

For most users:
- HTTP: `openapi/vaonis_instrument_http_api_openapi_fixed.yaml`
- Socket.IO: `asyncapi/vaonis_instrument_socket_api.asyncapi.yaml`
- Route catalog: `routes/http_routes_union.json`
- GUI/client schema bundle: `schemas/schema_bundle.json`

## Layout

- `openapi/`
  - HTTP OpenAPI variants from different extraction stages.
  - Prefer the `*_fixed.yaml` variant when in doubt.

- `asyncapi/`
  - Socket.IO events + command schemas.

- `schemas/`
  - `schemas/http/` - JSON Schemas for HTTP request/response models.
  - `schemas/events/` - server-emitted Socket.IO event payload schemas.
  - `schemas/socket/` - Socket.IO command request/response schemas.
  - `schemas/schema_bundle.json` - a single bundle used by the Tkinter GUI.

- `routes/`
  - `http_routes_union.json` - union of firmware HTTP routes (Stellina + Vespera baselines).
  - `HTTP_ROUTES.md` - human-readable listing.

- `mappings/`
  - `MAPPINGS_HTTP_ROUTES.md` - method+path -> generated `operationId` mapping.

- `reference/`
  - human-readable API references that explain connection, auth, and protocol expectations.

- `artifacts/`
  - raw connection strings, cloud URL hints, proto files.

- `manifests/` and `data/`
  - intermediate extraction outputs and convenience indexes.

## Regenerating the GUI schema bundle

The GUI expects a single consolidated schema bundle at `schemas/schema_bundle.json`.

From the repository root:

```bash
python tools/build_schema_bundle.py
```

## Versioning and compatibility

These artifacts are derived from specific Barnard + firmware baselines (see `docs/barnard-instrument-reference.md`).
Expect:
- optional/missing fields in status objects depending on state
- route and schema differences across firmware versions

When integrating, treat schemas as guidance and build defensively.
