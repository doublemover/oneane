# vaonis-barnard-instrument-sdk-extracted

Best-effort extraction of schemas and DTO definitions from the Barnard Android application (`com.vaonis.barnard`).

This package is primarily useful when you want:
- JSON Schema models for Barnard's HTTP request/response DTOs
- JSON Schema for Socket.IO event payloads (notably `STATUS_UPDATED`)
- lightweight TypeScript typings (`index.d.ts`) for the extracted types

The extracted schemas can be used independently of the HTTP/Socket clients in this repo.

## Install

```bash
npm install
```

Node 18+ is recommended.

## Exports

`src/index.js` exports:

- `schemas` - the full schema bundle
- `events` - event name -> schema reference convenience index
- `definitions` - schema `#/definitions/...` map
- `getEventSchema(eventName)` - returns the schema for a named event (when known)
- `getDefinition(defName)` - returns a definition object by its fully-qualified name

The raw bundle is also available in:
- `src/schemas.js`
- `src/schemas.json`

## Usage

```js
import { getEventSchema, getDefinition } from "./src/index.js";

const statusSchema = getEventSchema("STATUS_UPDATED");
const statusDef = getDefinition(
  "com.vaonis.instruments.sdk.models.status.StellinaStatus"
);

console.log(statusSchema?.$ref);
console.log(Object.keys(statusDef?.properties ?? {}));
```

## Documentation

- A concise overview of the extracted DTOs and event schemas is in:
  - `docs/SCHEMAS.md`

## Limitations

- This is **static analysis** of app code. Firmware behavior and schemas can vary by device model and firmware version.
- DTOs are treated as **optional-field** by default. In practice, the instrument may omit fields depending on state.
- Container element inference (`List<T>`, `Map<K,V>`) is best-effort.

If you need a more operational reference (endpoints, ports, auth), see:
- `docs/barnard-instrument-reference.md`
- `src/unified/reference/`
