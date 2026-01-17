# Vaonis instrument local API (extracted from Barnard)

This reference was generated from static analysis of the Android app `com.vaonis.barnard` (Barnard).

It focuses on the **local device control plane**: HTTP on port **8082** and Socket.IO on port **8083**.

Use this only with devices you own or have explicit permission to control.

## Connection parameters

Default (direct-to-device) values observed in the app:

- **Device IP**: `10.0.0.1`
- **HTTP base URL**: `http://10.0.0.1:8082/v1/`
- **Socket.IO URL**: `http://10.0.0.1:8083`
- **Socket.IO path**: `/socket.io`


The app also has *simulation* contexts that prepend `/stellina/http`, `/vespera/http`, `/stellina/socket`, `/vespera/socket` on the `ursa.dev.vaonis.com` host; see `StellinaContext$Companion` in the smali extraction if you need those.

## Authentication

Many write/control endpoints require an `Authorization` header. Barnard computes a **custom** `Basic ...` value using a server-provided challenge and a cryptographic signature.


For safety reasons, this archive does **not** include any proprietary key material or a drop-in auth generator. The generated client code therefore expects you to provide `Authorization` yourself.


Read-only endpoints like `GET /v1/app/getStatus` do not require auth and can be used to validate connectivity.

## HTTP endpoints

All paths below are relative to the HTTP base URL (default `http://10.0.0.1:8082`).


| Method | Path | Auth | Query | Body | Response | Operation |
|---|---|---|---|---|---|---|
| POST | `/v1/app/setSettings` | Yes | - | SettingsBody | OrderResponse | `updateSettings` |
| GET | `/v1/app/status` | No | - | - | StatusResponse | `getStatus` |
| POST | `/v1/board/requestShutdown` | Yes | - | - | OrderResponse | `requestShutdown` |
| POST | `/v1/capture/exportImageTiff` | Yes | - | TiffBody | TiffResponse | `exportTiff` |
| POST | `/v1/capture/setToBeResumable` | Yes | - | - | OrderResponse | `setToBeResumable` |
| POST | `/v1/captureStore/deleteStoredCapture` | Yes | - | DeleteStoredCaptureBody | OrderResponse | `deleteStoredCapture` |
| GET | `/v1/captureStore/getObservation` | No | storeId | - | StoredObservationResponse | `getStoredCaptureObservation` |
| POST | `/v1/captureStore/startObservationFromStoredCapture` | Yes | - | StartObservationFromStoredCaptureBody | OrderResponse | `startObservationFromStoredCapture` |
| POST | `/v1/darkManager/generateDark` | Yes | - | - | OrderResponse | `generateDark` |
| POST | `/v1/darkManager/stopGenerateDark` | Yes | - | - | OrderResponse | `stopGenerateDark` |
| POST | `/v1/expertMode/startStorageAcquisition` | Yes | - | StorageAcquisitionBody | OrderResponse | `startStorageAcquisition` |
| POST | `/v1/expertMode/stopStorageAcquisition` | Yes | - | - | OrderResponse | `stopStorageAcquisition` |
| POST | `/v1/general/adjustObservationFocus` | Yes | - | AdjustFocusBody | OrderResponse | `adjustObservationFocus` |
| POST | `/v1/general/adjustObservationFraming` | Yes | - | AdjustFramingBody | OrderResponse | `adjustObservationFraming` |
| POST | `/v1/general/openForMaintenance` | Yes | - | - | OrderResponse | `openArm` |
| POST | `/v1/general/park` | Yes | - | - | OrderResponse | `parkArm` |
| POST | `/v1/general/startAutoInit` | Yes | - | AutoInitBody | OrderResponse | `startAutoInit` |
| POST | `/v1/general/startObservation` | Yes | - | StartObservationBody | OrderResponse | `startObservation` |
| POST | `/v1/general/stopAutoInit` | Yes | - | - | OrderResponse | `stopAutoInit` |
| POST | `/v1/general/stopObservation` | Yes | - | - | OrderResponse | `stopObservation` |
| POST | `/v1/logs/consume` | Yes | - | - | LogResponse | `consumeLogs` |
| POST | `/v1/network/switchFrequency` | Yes | - | NetworkBody | Unit | `switchFrequency` |
| GET | `/v1/planner/getPlanObservation` | No | observationId | - | PlanObservationResponse | `getPlanObservation` |
| POST | `/v1/planner/startPlan` | Yes | - | PlanMyNightBody | OrderResponse | `startPlan` |
| POST | `/v1/planner/stopPlan` | Yes | - | - | OrderResponse | `stopPlan` |
| POST | `/v1/playlist/startPlaylist` | Yes | - | PlaylistBody | OrderResponse | `startPlaylist` |
| POST | `/v1/playlist/stopPlaylist` | Yes | - | - | OrderResponse | `stopPlaylist` |
| GET | `/v1/reporter/getAvailableReports` | No | - | - | ReportsResponse | `getAvailableReport` |
| POST | `/v1/reporter/markReportsAsSynced` | Yes | - | ReportsBody | Unit | `markReportsAsSynced` |
| POST | `/v1/storage/deleteUserStorageFolders` | Yes | - | DeleteUserStorageFolderBody | OrderResponse | `deleteUserStorageFolder` |
| GET | `/v1/storage/userStorageFolderContent` | No | folderPath | - | FolderContentResponse | `getStorageFolderContent` |
| POST | `/v1/sun/changePov` | Yes | - | SunModePovBody | OrderResponse | `changePov` |
| POST | `/v1/sun/handleUserAction` | Yes | - | SunModeActionBody | OrderResponse | `sendSunModeAction` |
| POST | `/v1/sun/restartAutofocus` | Yes | - | - | OrderResponse | `restartSunAutofocus` |
| POST | `/v1/sun/setUserParams` | Yes | - | SunModeParamsBody | OrderResponse | `setSunModeParams` |
| POST | `/v1/sun/startSunMode` | Yes | - | SunModeBody | OrderResponse | `startSunMode` |
| POST | `/v1/sun/stopObservation` | Yes | - | - | OrderResponse | `stopSunObservation` |
| POST | `/v1/updates/uploadUpdateFile` | Yes | fileName, model | - | ResponseBody | `uploadUpdateFile` |
| POST | `/v1/userManager/applyResetResponse` | Yes | - | RequestCodeBody | OrderResponse | `applyResetCode` |
| POST | `/v1/userManager/makeResetRequest` | Yes | - | - | ResetCodeResponse | `requestResetCode` |

Notes:
- `downloadImage` uses Retrofit `@Url` (dynamic full URL) and is omitted from the table; treat it as a generic streaming downloader.
- `updates/downloadUpdateFile` and `logs/getLogs` are **streaming**/binary responses.


## Request body models


### AdjustFocusBody

| Field | Type | JSON name |
|---|---|---|
| `restartCapture` | `Z` | `restartCapture` |

### AdjustFramingBody

| Field | Type | JSON name |
|---|---|---|
| `rot` | `D` | `rot` |
| `x` | `I` | `x` |
| `y` | `I` | `y` |

### RequestCodeBody

| Field | Type | JSON name |
|---|---|---|
| `response` | `String` | `response` |

### SunModePovBody

| Field | Type | JSON name |
|---|---|---|
| `pov` | `StellinaSunModeOperation$StellinaSunModePov` | `pov` |

### DeleteStoredCaptureBody

| Field | Type | JSON name |
|---|---|---|
| `storeId` | `String` | `storeId` |

### DeleteUserStorageFolderBody

| Field | Type | JSON name |
|---|---|---|
| `folderPaths` | `List` | `folderPaths` |

### TiffBody

| Field | Type | JSON name |
|---|---|---|
| `captureId` | `String` | `captureId` |

### ReportsBody

| Field | Type | JSON name |
|---|---|---|
| `reports` | `List` | `reports` |

### SunModeActionBody

| Field | Type | JSON name |
|---|---|---|
| `action` | `StellinaSunModeAction` | `action` |
| `pov` | `StellinaSunModeOperation$StellinaSunModePov` | `pov` |

### SunModeParamsBody

| Field | Type | JSON name |
|---|---|---|
| `MAP` | `Integer` | `MAP` |
| `exposureMicroSec` | `Integer` | `exposureMicroSec` |
| `exposureMode` | `StellinaObservationOperation$CurrentParams$ExposureMode` | `exposureMode` |
| `gain` | `Integer` | `gain` |

### AutoInitBody

| Field | Type | JSON name |
|---|---|---|
| `latitude` | `D` | `latitude` |
| `longitude` | `D` | `longitude` |
| `observatoryId` | `String` | `observatoryId` |
| `observatoryName` | `String` | `observatoryName` |
| `skipAutoFocus` | `Z` | `skipAutoFocus` |
| `time` | `J` | `time` |

### StartObservationBody

| Field | Type | JSON name |
|---|---|---|
| `algorithm` | `StellinaObservationOperation$StellinaPointingAlgorithm` | `algorithm` |
| `backgroundEnabled` | `Boolean` | `backgroundEnabled` |
| `backgroundPolyorder` | `Double` | `backgroundPolyorder` |
| `brightZoneOffset` | `StellinaObservationOperation$StellinaBrightZoneOffset` | `brightZoneOffset` |
| `de` | `Double` | `de` |
| `doStacking` | `Boolean` | `doStacking` |
| `exposureMicroSec` | `Integer` | `exposureMicroSec` |
| `gain` | `Integer` | `gain` |
| `hdrBackground` | `HdrBackgroundBody` | `hdrBackground` |
| `histogramEnabled` | `Boolean` | `histogramEnabled` |
| `histogramHigh` | `Double` | `histogramHigh` |
| `histogramLow` | `Double` | `histogramLow` |
| `histogramMedium` | `Double` | `histogramMedium` |
| `mosaicBody` | `MosaicBody` | `mosaicBody` |
| `objectId` | `String` | `objectId` |
| `objectName` | `String` | `objectName` |
| `objectType` | `String` | `objectType` |
| `observationType` | `StellinaObservationOperation$StellinaObservationType` | `observationType` |
| `ra` | `Double` | `ra` |
| `rot` | `Double` | `rot` |
| `store` | `StellinaObservationOperation$StellingCaptureStore` | `store` |
| `targetType` | `StellinaObservationOperation$ObservationTargetType` | `targetType` |

### StartObservationFromStoredCaptureBody

| Field | Type | JSON name |
|---|---|---|
| `storeId` | `String` | `storeId` |

### PlanMyNightBody

| Field | Type | JSON name |
|---|---|---|
| `appVersion` | `String` | `appVersion` |
| `deviceId` | `String` | `deviceId` |
| `latitude` | `D` | `latitude` |
| `longitude` | `D` | `longitude` |
| `observatoryId` | `String` | `observatoryId` |
| `observatoryName` | `String` | `observatoryName` |
| `planId` | `String` | `planId` |
| `planName` | `String` | `planName` |
| `planVersion` | `String` | `planVersion` |
| `targets` | `List` | `targets` |
| `userId` | `I` | `userId` |

### PlaylistBody

| Field | Type | JSON name |
|---|---|---|
| `appVersion` | `String` | `appVersion` |
| `deviceId` | `String` | `deviceId` |
| `playlistType` | `StellinaPlaylistOperation$PlaylistType` | `playlistType` |
| `targets` | `List` | `targets` |
| `userId` | `Integer` | `userId` |

### StorageAcquisitionBody

| Field | Type | JSON name |
|---|---|---|
| `exposureMicroSec` | `I` | `exposureMicroSec` |
| `flip` | `StorageAcquisitionBody$StellinaAcquisitionFlip` | `flip` |
| `gain` | `I` | `gain` |
| `numExposures` | `I` | `numExposures` |
| `overwrite` | `Z` | `overwrite` |
| `path` | `String` | `path` |

### SunModeBody

| Field | Type | JSON name |
|---|---|---|
| `appVersion` | `String` | `appVersion` |
| `deviceId` | `String` | `deviceId` |
| `eclipse` | `Z` | `eclipse` |
| `latitude` | `D` | `latitude` |
| `longitude` | `D` | `longitude` |
| `observatoryId` | `String` | `observatoryId` |
| `observatoryName` | `String` | `observatoryName` |
| `skipAutoFocus` | `Z` | `skipAutoFocus` |
| `time` | `J` | `time` |
| `userId` | `Integer` | `userId` |

### NetworkBody

| Field | Type | JSON name |
|---|---|---|
| `band` | `String` | `band` |

### SettingsBody

| Field | Type | JSON name |
|---|---|---|
| `algoHdrBackground` | `StellinaSettings$BalensMode` | `algoHdrBackground` |
| `buttonBrightness` | `String` | `buttonBrightness` |
| `enableDarkUsage` | `Boolean` | `enableDarkUsage` |
| `enableDithering` | `Boolean` | `enableDithering` |
| `enableFullResolution` | `Boolean` | `enableFullResolution` |
| `enableHdrBackground` | `Boolean` | `enableHdrBackground` |
| `enableLiveFocus` | `Boolean` | `enableLiveFocus` |
| `storageFileCategories` | `List` | `storageFileCategories` |
| `telescopeName` | `String` | `telescopeName` |
| `usbFileTypes` | `List` | `usbFileTypes` |

## Response models


### OrderResponse

| Field | Type | JSON name |
|---|---|---|
| `success` | `Z` | `success` |

### LogResponse

| Field | Type | JSON name |
|---|---|---|
| `file` | `String` | `file` |
| `result` | `LogResponse$Result` | `result` |
| `success` | `Z` | `success` |

### TiffResponse

| Field | Type | JSON name |
|---|---|---|
| `result` | `TiffData` | `result` |

### ReportsResponse

| Field | Type | JSON name |
|---|---|---|
| `result` | `List` | `result` |

### PlanObservationResponse

| Field | Type | JSON name |
|---|---|---|
| `result` | `StellinaObservationOperation` | `result` |
| `success` | `Z` | `success` |

### StatusResponse

| Field | Type | JSON name |
|---|---|---|
| `result` | `StellinaStatus` | `result` |
| `success` | `Z` | `success` |

### FolderContentResponse

| Field | Type | JSON name |
|---|---|---|
| `result` | `StellinaStorageFolderContent` | `result` |

### StoredObservationResponse

| Field | Type | JSON name |
|---|---|---|
| `result` | `StellinaObservationOperation` | `result` |
| `success` | `Z` | `success` |

### ResetCodeResponse

| Field | Type | JSON name |
|---|---|---|
| `result` | `String` | `result` |

## Socket.IO

Barnard uses a Socket.IO client (Engine.IO) for live status updates and control coordination.


Default connect parameters:
- URL: `http://10.0.0.1:8083`
- Path: `/socket.io`
- Query: `id={deviceId}&name={name}&countryCode={countryCode}`


Observed events:
- `STATUS_UPDATED` → payload is a JSON object (status snapshot)
- `CONTROL_ERROR` → payload indicates control/locking errors


Observed outbound messages (emitted on event name `message`):
- `takeControl` (no payload)
- `releaseControl` (no payload)
- `setSystemTime` (payload: integer/long milliseconds)
- `setUserName` (payload: `{ "device": "<deviceId>", "user": "<name or null>" }`)
