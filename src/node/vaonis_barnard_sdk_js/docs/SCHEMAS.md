# Extracted instrument SDK schemas (Barnard Android app)

This directory documents the JSON Schema bundle extracted from the Barnard Android app (`com.vaonis.barnard`).

Use this bundle when you need:
- request/response DTO shapes used by Barnard's instrument HTTP API client
- status and event payload shapes for Socket.IO (`STATUS_UPDATED`)
- TypeScript typings (generated from the same extraction)

If you want the repo's **corrected/normalized** schemas (used by the GUI and unified client), see:
- `src/unified/schemas/`

## Where the bundle lives

- Canonical bundle: `src/schemas.js`
- Raw JSON: `src/schemas.json`

The `src/index.js` entrypoint exposes convenience helpers:

```js
import { schemas, events, definitions, getEventSchema, getDefinition } from "../src/index.js";
```

## Events

Known Socket.IO server-emitted events:

- `STATUS_UPDATED`
  - Payload schema: `#/definitions/com.vaonis.instruments.sdk.models.status.StellinaStatus`
- `CONTROL_ERROR`
  - Payload: untyped / not reliably inferred from app code (exposed as a raw args array)

### Example: resolving the STATUS_UPDATED schema

```js
import { getEventSchema, getDefinition } from "../src/index.js";

const eventSchema = getEventSchema("STATUS_UPDATED");
const statusSchema = getDefinition(
  "com.vaonis.instruments.sdk.models.status.StellinaStatus"
);

console.log(eventSchema);
console.log(Object.keys(statusSchema.properties ?? {}));
```

## STATUS_UPDATED payload

Barnard parses `STATUS_UPDATED` into `com.vaonis.instruments.sdk.models.status.StellinaStatus`.

Important notes:
- Treat most fields as **optional**. The instrument omits keys depending on state and firmware.
- Nested objects and enums are referenced via `#/definitions/...`.

Top-level keys (best-effort; non-exhaustive):

- `apiVersion`: string
- `autofocusPosition`: integer
- `autofocusTemperature`: number
- `availableReports`: integer
- `boardError`: `#/definitions/com.vaonis.instruments.sdk.models.status.StellinaError`
- `boardInDebugMode`: boolean
- `boardInitError`: `#/definitions/com.vaonis.instruments.sdk.models.status.StellinaError`
- `bootCount`: integer
- `captureStore`: `#/definitions/com.vaonis.instruments.sdk.models.status.operations.StellinaCaptureStore`
- `challenge`: string
- `connectedDevices`: array of `#/definitions/com.vaonis.instruments.sdk.models.status.StellinaConnectedDevice`
- `currentOperation`: `#/definitions/com.vaonis.instruments.sdk.models.status.operations.StellinaOperation`
- `dark`: `#/definitions/com.vaonis.instruments.sdk.models.status.operations.StellinaDark`
- `elapsedTime`: integer
- `filter`: `#/definitions/com.vaonis.instruments.sdk.models.status.InstrumentFilter`
- `initError`: `#/definitions/com.vaonis.instruments.sdk.models.status.StellinaError`
- `initialized`: boolean
- `internalBattery`: `#/definitions/com.vaonis.instruments.sdk.models.status.InternalBattery`
- `logs`: `#/definitions/com.vaonis.instruments.sdk.models.status.StellinaLogs`
- `masterDeviceId`: string
- `model`: `#/definitions/com.vaonis.instruments.sdk.models.status.InstrumentModel`
- `motors`: `#/definitions/com.vaonis.instruments.sdk.models.status.StellinaMotors`
- `network`: `#/definitions/com.vaonis.instruments.sdk.models.status.StellinaNetwork`
- `observatoryId`: string
- `otherCurrentOperations`: array of `#/definitions/com.vaonis.instruments.sdk.models.status.operations.StellinaOperation`
- `position`: `#/definitions/com.vaonis.instruments.sdk.models.status.StellinaGeoPosition`
- `previousBootError`: `#/definitions/com.vaonis.instruments.sdk.models.status.StellinaError`
- `previousOperations`: `#/definitions/com.vaonis.instruments.sdk.models.status.operations.StellinaOperationMap`
- `sensors`: `#/definitions/com.vaonis.instruments.sdk.models.status.StellinaSensors`
- `settings`: `#/definitions/com.vaonis.instruments.sdk.models.status.StellinaSettings`
- `shuttingDown`: boolean
- `storage`: `#/definitions/com.vaonis.instruments.sdk.models.status.StellinaStorage`
- `telescopeId`: string
- `timestamp`: integer
- `update`: `#/definitions/com.vaonis.instruments.sdk.models.status.StellinaUpdateStatus`
- `version`: string
- `versionNumber`: `#/definitions/io.github.g00fy2.versioncompare.Version`

## Extracted request body DTOs

DTO classes extracted under `com.vaonis.instruments.sdk.models.body.*`:

- `com.vaonis.instruments.sdk.models.body.AdjustFocusBody`
- `com.vaonis.instruments.sdk.models.body.AdjustFramingBody`
- `com.vaonis.instruments.sdk.models.body.AutoInitBody`
- `com.vaonis.instruments.sdk.models.body.DeleteStoredCaptureBody`
- `com.vaonis.instruments.sdk.models.body.DeleteUserStorageFolderBody`
- `com.vaonis.instruments.sdk.models.body.HdrBackgroundBody`
- `com.vaonis.instruments.sdk.models.body.NetworkBody`
- `com.vaonis.instruments.sdk.models.body.PlaylistBody`
- `com.vaonis.instruments.sdk.models.body.PlaylistBody$TargetsParam`
- `com.vaonis.instruments.sdk.models.body.ReportsBody`
- `com.vaonis.instruments.sdk.models.body.ReportsBody$Report`
- `com.vaonis.instruments.sdk.models.body.RequestCodeBody`
- `com.vaonis.instruments.sdk.models.body.SettingsBody`
- `com.vaonis.instruments.sdk.models.body.StartObservationBody`
- `com.vaonis.instruments.sdk.models.body.StartObservationFromStoredCaptureBody`
- `com.vaonis.instruments.sdk.models.body.StorageAcquisitionBody`
- `com.vaonis.instruments.sdk.models.body.StorageAcquisitionBody$StellinaAcquisitionFlip`
- `com.vaonis.instruments.sdk.models.body.SunModeActionBody`
- `com.vaonis.instruments.sdk.models.body.SunModeBody`
- `com.vaonis.instruments.sdk.models.body.SunModeParamsBody`
- `com.vaonis.instruments.sdk.models.body.SunModePovBody`
- `com.vaonis.instruments.sdk.models.body.TiffBody`
- `com.vaonis.instruments.sdk.models.body.mosaic.MosaicBody`
- `com.vaonis.instruments.sdk.models.body.planmynight.PlanMyNightBody`
- `com.vaonis.instruments.sdk.models.body.planmynight.PlanMyNightTargetBody`

## Extracted response DTOs

DTO classes extracted under `com.vaonis.instruments.sdk.models.response.*`:

- `com.vaonis.instruments.sdk.models.response.FolderContentResponse`
- `com.vaonis.instruments.sdk.models.response.LogResponse`
- `com.vaonis.instruments.sdk.models.response.LogResponse$Result`
- `com.vaonis.instruments.sdk.models.response.OrderResponse`
- `com.vaonis.instruments.sdk.models.response.PlanObservationResponse`
- `com.vaonis.instruments.sdk.models.response.ReportsResponse`
- `com.vaonis.instruments.sdk.models.response.ResetCodeResponse`
- `com.vaonis.instruments.sdk.models.response.StatusResponse`
- `com.vaonis.instruments.sdk.models.response.StoredObservationResponse`
- `com.vaonis.instruments.sdk.models.response.TiffData`
- `com.vaonis.instruments.sdk.models.response.TiffResponse`

## Limitations

- This is derived from the app's SDK types; firmware-side schemas may be richer, stricter, or simply different.
- Generic collection element types are inferred heuristically; when inference is unreliable, schemas may omit `items` / `additionalProperties`.
