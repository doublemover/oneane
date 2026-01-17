// Auto-generated from Barnard Android app DEX (Vaonis instrument SDK)
// This file is best-effort and treats all object properties as optional.

export interface com_vaonis_instruments_sdk_models_body_AdjustFocusBody {
  "restartCapture"?: boolean;
}

export interface com_vaonis_instruments_sdk_models_body_AdjustFramingBody {
  "rot"?: number;
  "x"?: number;
  "y"?: number;
}

export interface com_vaonis_instruments_sdk_models_body_AutoInitBody {
  "latitude"?: number;
  "longitude"?: number;
  "observatoryId"?: string;
  "observatoryName"?: string;
  "skipAutoFocus"?: boolean;
  "time"?: number;
}

export interface com_vaonis_instruments_sdk_models_body_DeleteStoredCaptureBody {
  "storeId"?: string;
}

export interface com_vaonis_instruments_sdk_models_body_DeleteUserStorageFolderBody {
  "folderPaths"?: unknown[];
}

export interface com_vaonis_instruments_sdk_models_body_HdrBackgroundBody {
  "curve"?: number;
  "polynomialOrder"?: number;
  "ratioParam"?: number;
  "ratioParamLocal"?: number;
  "saturation"?: number;
  "whiteMeanNoiseRatio"?: number;
}

export interface com_vaonis_instruments_sdk_models_body_NetworkBody {
  "band"?: string;
}

export interface com_vaonis_instruments_sdk_models_body_PlaylistBody {
  "appVersion"?: string;
  "deviceId"?: string;
  "playlistType"?: com_vaonis_instruments_sdk_models_status_operations_StellinaPlaylistOperation_PlaylistType;
  "targets"?: com_vaonis_instruments_sdk_models_body_PlaylistBody_TargetsParam[];
  "userId"?: number;
}

export interface com_vaonis_instruments_sdk_models_body_PlaylistBody_TargetsParam {
  "params"?: com_vaonis_instruments_sdk_models_body_StartObservationBody;
}

export interface com_vaonis_instruments_sdk_models_body_ReportsBody {
  "reports"?: com_vaonis_instruments_sdk_models_body_ReportsBody_Report[];
}

export interface com_vaonis_instruments_sdk_models_body_ReportsBody_Report {
  "operationEnded"?: boolean;
  "operationId"?: string;
}

export interface com_vaonis_instruments_sdk_models_body_RequestCodeBody {
  "response"?: string;
}

export interface com_vaonis_instruments_sdk_models_body_SettingsBody {
  "algoHdrBackground"?: com_vaonis_instruments_sdk_models_status_StellinaSettings_BalensMode;
  "buttonBrightness"?: string;
  "enableDarkUsage"?: boolean;
  "enableDithering"?: boolean;
  "enableFullResolution"?: boolean;
  "enableHdrBackground"?: boolean;
  "enableLiveFocus"?: boolean;
  "storageFileCategories"?: unknown[];
  "telescopeName"?: string;
  "usbFileTypes"?: unknown[];
}

export interface com_vaonis_instruments_sdk_models_body_StartObservationBody {
  "algorithm"?: com_vaonis_instruments_sdk_models_status_operations_StellinaObservationOperation_StellinaPointingAlgorithm;
  "backgroundEnabled"?: boolean;
  "backgroundPolyorder"?: number;
  "brightZoneOffset"?: com_vaonis_instruments_sdk_models_status_operations_StellinaObservationOperation_StellinaBrightZoneOffset;
  "de"?: number;
  "doStacking"?: boolean;
  "exposureMicroSec"?: number;
  "gain"?: number;
  "hdrBackground"?: com_vaonis_instruments_sdk_models_body_HdrBackgroundBody;
  "histogramEnabled"?: boolean;
  "histogramHigh"?: number;
  "histogramLow"?: number;
  "histogramMedium"?: number;
  "mosaicBody"?: com_vaonis_instruments_sdk_models_body_mosaic_MosaicBody;
  "objectId"?: string;
  "objectName"?: string;
  "objectType"?: string;
  "observationType"?: com_vaonis_instruments_sdk_models_status_operations_StellinaObservationOperation_StellinaObservationType;
  "ra"?: number;
  "rot"?: number;
  "store"?: com_vaonis_instruments_sdk_models_status_operations_StellinaObservationOperation_StellingCaptureStore;
  "targetType"?: com_vaonis_instruments_sdk_models_status_operations_StellinaObservationOperation_ObservationTargetType;
}

export interface com_vaonis_instruments_sdk_models_body_StartObservationFromStoredCaptureBody {
  "storeId"?: string;
}

export interface com_vaonis_instruments_sdk_models_body_StorageAcquisitionBody {
  "exposureMicroSec"?: number;
  "flip"?: com_vaonis_instruments_sdk_models_body_StorageAcquisitionBody_StellinaAcquisitionFlip;
  "gain"?: number;
  "numExposures"?: number;
  "overwrite"?: boolean;
  "path"?: string;
}

export type com_vaonis_instruments_sdk_models_body_StorageAcquisitionBody_StellinaAcquisitionFlip = "BOTH" | "FLIP" | "NO_FLIP";

export interface com_vaonis_instruments_sdk_models_body_SunModeActionBody {
  "action"?: com_vaonis_instruments_sdk_models_status_StellinaSunModeAction;
  "pov"?: com_vaonis_instruments_sdk_models_status_operations_StellinaSunModeOperation_StellinaSunModePov;
}

export interface com_vaonis_instruments_sdk_models_body_SunModeBody {
  "appVersion"?: string;
  "deviceId"?: string;
  "eclipse"?: boolean;
  "latitude"?: number;
  "longitude"?: number;
  "observatoryId"?: string;
  "observatoryName"?: string;
  "skipAutoFocus"?: boolean;
  "time"?: number;
  "userId"?: number;
}

export interface com_vaonis_instruments_sdk_models_body_SunModeParamsBody {
  "MAP"?: number;
  "exposureMicroSec"?: number;
  "exposureMode"?: com_vaonis_instruments_sdk_models_status_operations_StellinaObservationOperation_CurrentParams_ExposureMode;
  "gain"?: number;
}

export interface com_vaonis_instruments_sdk_models_body_SunModePovBody {
  "pov"?: com_vaonis_instruments_sdk_models_status_operations_StellinaSunModeOperation_StellinaSunModePov;
}

export interface com_vaonis_instruments_sdk_models_body_TiffBody {
  "captureId"?: string;
}

export interface com_vaonis_instruments_sdk_models_body_mosaic_MosaicBody {
  "heightDegree"?: number;
  "widthDegree"?: number;
}

export interface com_vaonis_instruments_sdk_models_body_planmynight_PlanMyNightBody {
  "appVersion"?: string;
  "deviceId"?: string;
  "latitude"?: number;
  "longitude"?: number;
  "observatoryId"?: string;
  "observatoryName"?: string;
  "planId"?: string;
  "planName"?: string;
  "planVersion"?: string;
  "targets"?: unknown[];
  "userId"?: number;
}

export interface com_vaonis_instruments_sdk_models_body_planmynight_PlanMyNightTargetBody {
  "endTime"?: number;
  "params"?: com_vaonis_instruments_sdk_models_body_StartObservationBody;
  "startTime"?: number;
  "storeId"?: string;
}

export interface com_vaonis_instruments_sdk_models_response_FolderContentResponse {
  "result"?: com_vaonis_instruments_sdk_models_status_StellinaStorageFolderContent;
}

export interface com_vaonis_instruments_sdk_models_response_LogResponse {
  "file"?: string;
  "result"?: com_vaonis_instruments_sdk_models_response_LogResponse_Result;
  "success"?: boolean;
}

export interface com_vaonis_instruments_sdk_models_response_LogResponse_Result {
  "data"?: string;
  "message"?: string;
}

export interface com_vaonis_instruments_sdk_models_response_OrderResponse {
  "success"?: boolean;
}

export interface com_vaonis_instruments_sdk_models_response_PlanObservationResponse {
  "result"?: com_vaonis_instruments_sdk_models_status_operations_StellinaObservationOperation;
  "success"?: boolean;
}

export interface com_vaonis_instruments_sdk_models_response_ReportsResponse {
  "result"?: unknown[];
}

export interface com_vaonis_instruments_sdk_models_response_ResetCodeResponse {
  "result"?: string;
}

export interface com_vaonis_instruments_sdk_models_response_StatusResponse {
  "result"?: com_vaonis_instruments_sdk_models_status_StellinaStatus;
  "success"?: boolean;
}

export interface com_vaonis_instruments_sdk_models_response_StoredObservationResponse {
  "result"?: com_vaonis_instruments_sdk_models_status_operations_StellinaObservationOperation;
  "success"?: boolean;
}

export interface com_vaonis_instruments_sdk_models_response_TiffData {
  "savedOnUsbStorage"?: boolean;
  "stackingCount"?: number;
  "url"?: string;
}

export interface com_vaonis_instruments_sdk_models_response_TiffResponse {
  "result"?: com_vaonis_instruments_sdk_models_response_TiffData;
}

export type com_vaonis_instruments_sdk_models_status_InstrumentFilter = "CLS" | "DUAL" | "DUST" | "IR" | "NONE" | "SOLAR";

export type com_vaonis_instruments_sdk_models_status_InstrumentModel = "stellina" | "vespera" | "vespera1ed" | "vespera2" | "vesperapro";

export type com_vaonis_instruments_sdk_models_status_InstrumentModelSettings = "BTN_BRIGHTNESS" | "DARKS" | "DITHERING" | "FULL_RESOLUTION" | "HDR_BACKGROUND" | "LIVE_FOCUS" | "WIFI_5GHZ";

export interface com_vaonis_instruments_sdk_models_status_InternalBattery {
  "chargeAlert"?: com_vaonis_instruments_sdk_models_status_InternalBattery_ChargeAlert;
  "chargeLevel"?: number;
  "chargeStatus"?: com_vaonis_instruments_sdk_models_status_InternalBattery_ChargeStatus;
}

export type com_vaonis_instruments_sdk_models_status_InternalBattery_ChargeAlert = "NONE" | "TOO_COLD" | "TOO_HOT";

export type com_vaonis_instruments_sdk_models_status_InternalBattery_ChargeStatus = "CHARGING" | "CONNECTED" | "OFF";

export interface com_vaonis_instruments_sdk_models_status_InternalBattery_Companion {
}

export interface com_vaonis_instruments_sdk_models_status_StellinaCameraInfo {
  "heightDeg"?: number;
  "heightPx"?: number;
  "maxDegreesField"?: number;
  "maxInstrumentField"?: number;
  "minInstrumentField"?: number;
  "name"?: string;
  "widthDeg"?: number;
  "widthPx"?: number;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaCameraInfo_Companion {
}

export interface com_vaonis_instruments_sdk_models_status_StellinaCapture {
  "acquisitionCount"?: number;
  "cameraParams"?: com_vaonis_instruments_sdk_models_status_StellinaCapture_StellinaCameraParams;
  "captureType"?: com_vaonis_instruments_sdk_models_status_StellinaCapture_StellinaCaptureType;
  "dark"?: boolean;
  "debayerInterpolation"?: com_vaonis_instruments_sdk_models_status_StellinaCapture_StellinaDebayerInterpolation;
  "endHumidity"?: number;
  "endTemperature"?: number;
  "endTime"?: number;
  "error"?: com_vaonis_instruments_sdk_models_status_StellinaError;
  "hasStacking"?: boolean;
  "id"?: string;
  "images"?: com_vaonis_instruments_sdk_models_status_StellinaCapture_StellinaCaptureImage[];
  "outputImageCount"?: number;
  "outputImageErrorCount"?: number;
  "stackingCount"?: number;
  "stackingErrorCount"?: number;
  "stackingErrorMap"?: com_vaonis_instruments_sdk_models_status_StellinaCapture_StellinaStackingErrorMap;
  "startHumidity"?: number;
  "startTemperature"?: number;
  "startTime"?: number;
  "target"?: com_vaonis_instruments_sdk_models_status_operations_StellinaObservationOperation_StellinaObservationTarget;
  "totalStackingCount"?: number;
  "userExposureMicroSec"?: number;
  "userGain"?: number;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaCapture_StackingDuration {
  "captureStackingDuration"?: number;
  "totalStackingDuration"?: number;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaCapture_StellinaCameraParams {
  "exposureMicroSec"?: number;
  "gain"?: number;
  "height"?: number;
  "width"?: number;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaCapture_StellinaCaptureImage {
  "cropHeight"?: number;
  "cropWidth"?: number;
  "cropX"?: number;
  "cropY"?: number;
  "exifSize"?: number;
  "index"?: number;
  "metadata"?: com_vaonis_instruments_sdk_models_status_StellinaCapture_StellinaCaptureImage_Metadata;
  "stackingCount"?: number;
  "stackingErrorCount"?: number;
  "url"?: string;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaCapture_StellinaCaptureImage_Metadata {
  "MAP"?: number;
  "exposureMicroSec"?: number;
  "gain"?: number;
  "hdrBackground"?: string;
  "mosaic"?: com_vaonis_instruments_sdk_models_status_StellinaCapture_StellinaCaptureImage_Metadata_Mosaic;
  "solar"?: com_vaonis_instruments_sdk_models_status_StellinaCapture_StellinaCaptureImage_Metadata_Solar;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaCapture_StellinaCaptureImage_Metadata_Mosaic {
  "turnCount"?: number;
  "turnProgress"?: number;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaCapture_StellinaCaptureImage_Metadata_Solar {
  "pov"?: com_vaonis_instruments_sdk_models_status_operations_StellinaSunModeOperation_StellinaSunModePov;
  "success"?: boolean;
}

export type com_vaonis_instruments_sdk_models_status_StellinaCapture_StellinaCaptureType = "ADJUST_FOCUS" | "ADJUST_FRAMING" | "INITIAL" | "MANUAL";

export type com_vaonis_instruments_sdk_models_status_StellinaCapture_StellinaDebayerInterpolation = "SUPER_PIXEL" | "VNG";

export interface com_vaonis_instruments_sdk_models_status_StellinaCapture_StellinaStackingErrorMap {
  "StackingBadRegistration"?: number;
  "StackingError"?: number;
  "StackingFitError"?: number;
  "StackingLackOfStar"?: number;
  "StackingMatchingError"?: number;
  "StackingRoundnessError"?: number;
  "total"?: number;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaConnectedDevice {
  "description"?: string;
  "id"?: string;
  "name"?: string;
  "userId"?: number;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaError {
  "name"?: string;
  "rawError"?: string;
  "unknownName"?: string;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaError_Companion {
}

export interface com_vaonis_instruments_sdk_models_status_StellinaGeoPosition {
  "latitude"?: number;
  "longitude"?: number;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaGeoPosition_Companion {
}

export interface com_vaonis_instruments_sdk_models_status_StellinaLogs {
  "bufferPosition"?: number;
  "bufferSize"?: number;
  "numFiles"?: number;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaMotors {
  "ALT"?: com_vaonis_instruments_sdk_models_status_StellinaMotors_StellinaMotorStatus;
  "AZ"?: com_vaonis_instruments_sdk_models_status_StellinaMotors_StellinaMotorStatus;
  "DER"?: com_vaonis_instruments_sdk_models_status_StellinaMotors_StellinaMotorStatus;
  "MAP"?: com_vaonis_instruments_sdk_models_status_StellinaMotors_StellinaMotorStatus;
  "isParked"?: boolean;
  "isPointingAboveHorizon"?: boolean;
  "isTracking"?: boolean;
}

export type com_vaonis_instruments_sdk_models_status_StellinaMotors_MotorState = "IDLE" | "MOVING" | "TRACKING";

export interface com_vaonis_instruments_sdk_models_status_StellinaMotors_StellinaMotorStatus {
  "atStop"?: boolean;
  "calibrated"?: boolean;
  "position"?: number;
  "state"?: com_vaonis_instruments_sdk_models_status_StellinaMotors_MotorState;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaNetwork {
  "band"?: string;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaReport {
  "bootCount"?: number;
  "observatoryId"?: string;
  "operation"?: com_vaonis_instruments_sdk_models_status_operations_StellinaOperation;
  "operationEnded"?: boolean;
  "position"?: com_vaonis_instruments_sdk_models_status_StellinaGeoPosition;
  "telescopeId"?: string;
  "timestamp"?: number;
  "version"?: string;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaReport_Companion {
}

export interface com_vaonis_instruments_sdk_models_status_StellinaSensors {
  "defogStatus"?: com_vaonis_instruments_sdk_models_status_StellinaSensors_DefogStatus;
  "dewpointDepression"?: number;
  "humidity"?: number;
  "humidityDelta"?: number;
  "temperature"?: number;
  "temperatureDelta"?: number;
}

export type com_vaonis_instruments_sdk_models_status_StellinaSensors_DefogStatus = "LOW_DD" | "LOW_TEMP" | "OFF" | "ON";

export interface com_vaonis_instruments_sdk_models_status_StellinaSettings {
  "algoHdrBackground"?: string;
  "buttonBrightness"?: string;
  "enableDarkUsage"?: boolean;
  "enableDithering"?: boolean;
  "enableFullResolution"?: boolean;
  "enableHdrBackground"?: boolean;
  "enableLiveFocus"?: boolean;
  "storageFileCategories"?: com_vaonis_instruments_sdk_models_status_StellinaSettings_StellinaStorageFileCategory[];
  "telescopeName"?: string;
  "usbFileTypes"?: unknown[];
}

export type com_vaonis_instruments_sdk_models_status_StellinaSettings_BalensMode = "HARD" | "OLD" | "RECOMMENDED" | "SOFT";

export interface com_vaonis_instruments_sdk_models_status_StellinaSettings_BalensMode_Companion {
}

export type com_vaonis_instruments_sdk_models_status_StellinaSettings_ButonLuminosity = "HIGH" | "LOW" | "MEDIUM";

export interface com_vaonis_instruments_sdk_models_status_StellinaSettings_ButonLuminosity_Companion {
}

export type com_vaonis_instruments_sdk_models_status_StellinaSettings_StellinaStorageFileCategory = "DEBUG" | "DIRECT" | "OUTPUT" | "RAW" | "TIFF";

export interface com_vaonis_instruments_sdk_models_status_StellinaSkyPosition {
  "de"?: number;
  "ra"?: number;
  "rot"?: number;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaStatus {
  "apiVersion"?: string;
  "autofocusPosition"?: number;
  "autofocusTemperature"?: number;
  "availableReports"?: number;
  "boardError"?: com_vaonis_instruments_sdk_models_status_StellinaError;
  "boardInDebugMode"?: boolean;
  "boardInitError"?: com_vaonis_instruments_sdk_models_status_StellinaError;
  "bootCount"?: number;
  "captureStore"?: com_vaonis_instruments_sdk_models_status_operations_StellinaCaptureStore;
  "challenge"?: string;
  "connectedDevices"?: com_vaonis_instruments_sdk_models_status_StellinaConnectedDevice[];
  "currentOperation"?: com_vaonis_instruments_sdk_models_status_operations_StellinaOperation;
  "dark"?: com_vaonis_instruments_sdk_models_status_operations_StellinaDark;
  "elapsedTime"?: number;
  "filter"?: com_vaonis_instruments_sdk_models_status_InstrumentFilter;
  "initError"?: com_vaonis_instruments_sdk_models_status_StellinaError;
  "initialized"?: boolean;
  "internalBattery"?: com_vaonis_instruments_sdk_models_status_InternalBattery;
  "logs"?: com_vaonis_instruments_sdk_models_status_StellinaLogs;
  "masterDeviceId"?: string;
  "model"?: com_vaonis_instruments_sdk_models_status_InstrumentModel;
  "motors"?: com_vaonis_instruments_sdk_models_status_StellinaMotors;
  "network"?: com_vaonis_instruments_sdk_models_status_StellinaNetwork;
  "observatoryId"?: string;
  "otherCurrentOperations"?: com_vaonis_instruments_sdk_models_status_operations_StellinaOperation[];
  "position"?: com_vaonis_instruments_sdk_models_status_StellinaGeoPosition;
  "previousBootError"?: com_vaonis_instruments_sdk_models_status_StellinaError;
  "previousOperations"?: com_vaonis_instruments_sdk_models_status_operations_StellinaOperationMap;
  "sensors"?: com_vaonis_instruments_sdk_models_status_StellinaSensors;
  "settings"?: com_vaonis_instruments_sdk_models_status_StellinaSettings;
  "shuttingDown"?: boolean;
  "storage"?: com_vaonis_instruments_sdk_models_status_StellinaStorage;
  "telescopeId"?: string;
  "timestamp"?: number;
  "update"?: com_vaonis_instruments_sdk_models_status_StellinaUpdateStatus;
  "version"?: string;
  "versionNumber"?: io_github_g00fy2_versioncompare_Version;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaStatus_WhenMappings {
}

export interface com_vaonis_instruments_sdk_models_status_StellinaStatus_apiVersion_2 {
  "this$0"?: com_vaonis_instruments_sdk_models_status_StellinaStatus;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaStatus_autofocusPosition_2 {
  "this$0"?: com_vaonis_instruments_sdk_models_status_StellinaStatus;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaStatus_autofocusTemperature_2 {
  "this$0"?: com_vaonis_instruments_sdk_models_status_StellinaStatus;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaStatus_availableReports_2 {
  "this$0"?: com_vaonis_instruments_sdk_models_status_StellinaStatus;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaStatus_boardError_2 {
  "this$0"?: com_vaonis_instruments_sdk_models_status_StellinaStatus;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaStatus_boardInDebugMode_2 {
  "this$0"?: com_vaonis_instruments_sdk_models_status_StellinaStatus;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaStatus_boardInitError_2 {
  "this$0"?: com_vaonis_instruments_sdk_models_status_StellinaStatus;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaStatus_bootCount_2 {
  "this$0"?: com_vaonis_instruments_sdk_models_status_StellinaStatus;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaStatus_captureStore_2 {
  "this$0"?: com_vaonis_instruments_sdk_models_status_StellinaStatus;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaStatus_challenge_2 {
  "this$0"?: com_vaonis_instruments_sdk_models_status_StellinaStatus;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaStatus_connectedDevices_2 {
  "this$0"?: com_vaonis_instruments_sdk_models_status_StellinaStatus;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaStatus_currentOperation_2 {
  "this$0"?: com_vaonis_instruments_sdk_models_status_StellinaStatus;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaStatus_dark_2 {
  "this$0"?: com_vaonis_instruments_sdk_models_status_StellinaStatus;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaStatus_elapsedTime_2 {
  "this$0"?: com_vaonis_instruments_sdk_models_status_StellinaStatus;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaStatus_filter_2 {
  "this$0"?: com_vaonis_instruments_sdk_models_status_StellinaStatus;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaStatus_initError_2 {
  "this$0"?: com_vaonis_instruments_sdk_models_status_StellinaStatus;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaStatus_initialized_2 {
  "this$0"?: com_vaonis_instruments_sdk_models_status_StellinaStatus;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaStatus_internalBattery_2 {
  "this$0"?: com_vaonis_instruments_sdk_models_status_StellinaStatus;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaStatus_logs_2 {
  "this$0"?: com_vaonis_instruments_sdk_models_status_StellinaStatus;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaStatus_masterDeviceId_2 {
  "this$0"?: com_vaonis_instruments_sdk_models_status_StellinaStatus;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaStatus_model_2 {
  "this$0"?: com_vaonis_instruments_sdk_models_status_StellinaStatus;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaStatus_motors_2 {
  "this$0"?: com_vaonis_instruments_sdk_models_status_StellinaStatus;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaStatus_network_2 {
  "this$0"?: com_vaonis_instruments_sdk_models_status_StellinaStatus;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaStatus_observatoryId_2 {
  "this$0"?: com_vaonis_instruments_sdk_models_status_StellinaStatus;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaStatus_otherCurrentOperations_2 {
  "this$0"?: com_vaonis_instruments_sdk_models_status_StellinaStatus;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaStatus_position_2 {
  "this$0"?: com_vaonis_instruments_sdk_models_status_StellinaStatus;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaStatus_previousBootError_2 {
  "this$0"?: com_vaonis_instruments_sdk_models_status_StellinaStatus;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaStatus_previousOperations_2 {
  "this$0"?: com_vaonis_instruments_sdk_models_status_StellinaStatus;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaStatus_sensors_2 {
  "this$0"?: com_vaonis_instruments_sdk_models_status_StellinaStatus;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaStatus_settings_2 {
  "this$0"?: com_vaonis_instruments_sdk_models_status_StellinaStatus;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaStatus_shuttingDown_2 {
  "this$0"?: com_vaonis_instruments_sdk_models_status_StellinaStatus;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaStatus_storage_2 {
  "this$0"?: com_vaonis_instruments_sdk_models_status_StellinaStatus;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaStatus_telescopeId_2 {
  "this$0"?: com_vaonis_instruments_sdk_models_status_StellinaStatus;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaStatus_timestamp_2 {
  "this$0"?: com_vaonis_instruments_sdk_models_status_StellinaStatus;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaStatus_update_2 {
  "this$0"?: com_vaonis_instruments_sdk_models_status_StellinaStatus;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaStatus_version_2 {
  "this$0"?: com_vaonis_instruments_sdk_models_status_StellinaStatus;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaStatus_versionNumber_2 {
  "this$0"?: com_vaonis_instruments_sdk_models_status_StellinaStatus;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaStorage {
  "data"?: com_vaonis_instruments_sdk_models_status_StellinaStorage_StellinaStorageSpace;
  "public"?: com_vaonis_instruments_sdk_models_status_StellinaStorage_StellinaStorageSpace;
  "system"?: com_vaonis_instruments_sdk_models_status_StellinaStorage_StellinaStorageSpace;
  "usb"?: com_vaonis_instruments_sdk_models_status_StellinaStorage_StellinaStorageSpace;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaStorage_StellinaStorageSpace {
  "available"?: number;
  "changeCount"?: number;
  "required"?: number;
  "size"?: number;
  "system"?: number;
  "user"?: number;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaStorageFolderContent {
  "fileCountPerType"?: Record<string, unknown>;
  "folders"?: com_vaonis_instruments_sdk_models_status_StellinaStorageFolderContent[];
  "name"?: string;
  "size"?: number;
}

export type com_vaonis_instruments_sdk_models_status_StellinaStorageFolderContent_FileType = "FITS" | "JPEG" | "JSON" | "OTHER" | "TIFF";

export type com_vaonis_instruments_sdk_models_status_StellinaSunModeAction = "CANCEL_FILTER_REMOVAL" | "CONFIRM_ARM_ORIENTATION" | "CONFIRM_FILTER_INSTALLATION" | "CONFIRM_FILTER_REMOVED" | "DISABLE_SAFETY" | "ENABLE_SAFETY" | "PREPARE_FILTER_REMOVAL" | "RETRY_AFTER_FAILURE";

export interface com_vaonis_instruments_sdk_models_status_StellinaUpdateStatus {
  "installedVersion"?: string;
  "minimumCompatibleVersion"?: string;
  "progressInfo"?: com_vaonis_instruments_sdk_models_status_StellinaUpdateStatus_StellinaUpdateProgressInfo;
  "state"?: com_vaonis_instruments_sdk_models_status_StellinaUpdateStatus_StellinaUpdateState;
}

export interface com_vaonis_instruments_sdk_models_status_StellinaUpdateStatus_StellinaUpdateProgressInfo {
  "progressPercent"?: number;
  "step"?: number;
  "stepTotal"?: number;
}

export type com_vaonis_instruments_sdk_models_status_StellinaUpdateStatus_StellinaUpdateState = "IDLE" | "INSTALL" | "UPLOAD";

export type com_vaonis_instruments_sdk_models_status_operations_CalibrationStep = "BIAS_ACQUISITION" | "DARK_ACQUISITION" | "MASTER_DARK_GENERATION";

export interface com_vaonis_instruments_sdk_models_status_operations_DarkCalibrationStep {
  "progress"?: number;
  "type"?: string;
}

export interface com_vaonis_instruments_sdk_models_status_operations_StellinaAutoInitOperation {
  "appVersion"?: string;
  "armPosition"?: com_vaonis_instruments_sdk_models_status_operations_StellinaAutoInitOperation_StellinaAutoInitArmPosition;
  "astrometry"?: com_vaonis_instruments_sdk_models_status_StellinaSkyPosition;
  "deviceId"?: string;
  "endTime"?: number;
  "error"?: com_vaonis_instruments_sdk_models_status_StellinaError;
  "focusResult"?: com_vaonis_instruments_sdk_models_status_operations_StellinaAutoInitOperation_AutofocusResult;
  "id"?: string;
  "observatoryId"?: string;
  "observatoryName"?: string;
  "position"?: com_vaonis_instruments_sdk_models_status_StellinaGeoPosition;
  "startTime"?: number;
  "steps"?: com_vaonis_instruments_sdk_models_status_operations_StellinaAutoInitOperation_StellinaAutoInitStep[];
  "stopped"?: boolean;
  "time"?: number;
  "type"?: com_vaonis_instruments_sdk_models_status_operations_StellinaOperationType;
  "userId"?: number;
}

export interface com_vaonis_instruments_sdk_models_status_operations_StellinaAutoInitOperation_AutofocusResult {
  "focusValue"?: number;
  "map"?: number;
}

export interface com_vaonis_instruments_sdk_models_status_operations_StellinaAutoInitOperation_StellinaAutoInitArmPosition {
  "ALT"?: number;
  "AZ"?: number;
  "index"?: number;
}

export interface com_vaonis_instruments_sdk_models_status_operations_StellinaAutoInitOperation_StellinaAutoInitStep {
  "progress"?: number;
  "steps"?: com_vaonis_instruments_sdk_models_status_operations_CalibrationStep[];
  "type"?: com_vaonis_instruments_sdk_models_status_operations_StellinaAutoInitOperation_StellinaAutoInitStepType;
}

export type com_vaonis_instruments_sdk_models_status_operations_StellinaAutoInitOperation_StellinaAutoInitStepType = "ASTROMETRY" | "AUTO_FOCUS" | "MOVING" | "OPEN_ARM" | "PREPARE_MC_BOARD" | "RETRY_ASTROMETRY" | "SEEK_STOP" | "START_TRACKING" | "TRY_POSITION" | "WIDE_AUTOFOCUS_FAILED_ASTROMETRY" | "WIDE_AUTOFOCUS_NO_FACTORY";

export interface com_vaonis_instruments_sdk_models_status_operations_StellinaCaptureStore {
  "storedCaptures"?: com_vaonis_instruments_sdk_models_status_operations_StellinaCaptureStore_StellinaStoredCapture[];
}

export interface com_vaonis_instruments_sdk_models_status_operations_StellinaCaptureStore_StellinaStoredCapture {
  "dark"?: boolean;
  "error"?: com_vaonis_instruments_sdk_models_status_StellinaError;
  "exposureMicroSec"?: number;
  "filter"?: com_vaonis_instruments_sdk_models_status_InstrumentFilter;
  "lastImage"?: com_vaonis_instruments_sdk_models_status_StellinaCapture_StellinaCaptureImage;
  "mosaic"?: com_vaonis_instruments_sdk_models_body_mosaic_MosaicBody;
  "startTime"?: number;
  "storeId"?: string;
  "target"?: com_vaonis_instruments_sdk_models_status_operations_StellinaObservationOperation_StellinaObservationTarget;
  "totalStackingCount"?: number;
}

export interface com_vaonis_instruments_sdk_models_status_operations_StellinaDark {
  "date"?: number;
  "version"?: string;
}

export interface com_vaonis_instruments_sdk_models_status_operations_StellinaDarkCalibrationOperation {
  "appVersion"?: string;
  "ctx"?: string;
  "deviceId"?: string;
  "endTime"?: number;
  "error"?: com_vaonis_instruments_sdk_models_status_StellinaError;
  "id"?: string;
  "startTime"?: number;
  "steps"?: com_vaonis_instruments_sdk_models_status_operations_DarkCalibrationStep[];
  "stopped"?: boolean;
  "type"?: com_vaonis_instruments_sdk_models_status_operations_StellinaOperationType;
  "userId"?: number;
}

export interface com_vaonis_instruments_sdk_models_status_operations_StellinaDeleteFoldersOperation {
  "appVersion"?: string;
  "deletedFolderCount"?: number;
  "deviceId"?: string;
  "endTime"?: number;
  "error"?: com_vaonis_instruments_sdk_models_status_StellinaError;
  "id"?: string;
  "startTime"?: number;
  "stopped"?: boolean;
  "totalFolderCount"?: number;
  "type"?: com_vaonis_instruments_sdk_models_status_operations_StellinaOperationType;
  "userId"?: number;
}

export interface com_vaonis_instruments_sdk_models_status_operations_StellinaObservationOperation {
  "actionInProgress"?: boolean;
  "appVersion"?: string;
  "capture"?: com_vaonis_instruments_sdk_models_status_StellinaCapture;
  "currentParams"?: com_vaonis_instruments_sdk_models_status_operations_StellinaObservationOperation_CurrentParams;
  "deviceId"?: string;
  "eclipse"?: boolean;
  "endTime"?: number;
  "error"?: com_vaonis_instruments_sdk_models_status_StellinaError;
  "filter"?: com_vaonis_instruments_sdk_models_status_InstrumentFilter;
  "focusWarning"?: boolean;
  "framing"?: com_vaonis_instruments_sdk_models_status_StellinaSkyPosition;
  "id"?: string;
  "isRestored"?: boolean;
  "mosaic"?: com_vaonis_instruments_sdk_models_body_mosaic_MosaicBody;
  "observationType"?: com_vaonis_instruments_sdk_models_status_operations_StellinaObservationOperation_StellinaObservationType;
  "povErrorRatio"?: number;
  "previousCaptures"?: com_vaonis_instruments_sdk_models_status_StellinaCapture[];
  "startTime"?: number;
  "steps"?: com_vaonis_instruments_sdk_models_status_operations_StellinaObservationOperation_StellinaObservationStep[];
  "stopped"?: boolean;
  "store"?: com_vaonis_instruments_sdk_models_status_operations_StellinaObservationOperation_StellingCaptureStore;
  "target"?: com_vaonis_instruments_sdk_models_status_operations_StellinaObservationOperation_StellinaObservationTarget;
  "type"?: com_vaonis_instruments_sdk_models_status_operations_StellinaOperationType;
  "userId"?: number;
}

export interface com_vaonis_instruments_sdk_models_status_operations_StellinaObservationOperation_CurrentParams {
  "MAP"?: number;
  "exposureMicroSec"?: number;
  "exposureMode"?: com_vaonis_instruments_sdk_models_status_operations_StellinaObservationOperation_CurrentParams_ExposureMode;
  "gain"?: number;
}

export type com_vaonis_instruments_sdk_models_status_operations_StellinaObservationOperation_CurrentParams_ExposureMode = "antique" | "auto" | "init" | "static" | "user";

export type com_vaonis_instruments_sdk_models_status_operations_StellinaObservationOperation_ObservationTargetType = "CATALOG" | "DEBUG_UI" | "MANUAL";

export type com_vaonis_instruments_sdk_models_status_operations_StellinaObservationOperation_StellinaBrightZoneOffset = "AUTO" | "FAR" | "NEAR";

export type com_vaonis_instruments_sdk_models_status_operations_StellinaObservationOperation_StellinaCaptureStoreState = "NON_RESUMABLE" | "PLAN" | "RESUME" | "TO_BE_RESUMABLE";

export interface com_vaonis_instruments_sdk_models_status_operations_StellinaObservationOperation_StellinaHdrBackgroundParams {
  "curve"?: number;
  "polynomialOrder"?: number;
  "ratioParam"?: number;
  "ratioParamLocal"?: number;
  "saturation"?: number;
  "whiteMeanNoiseRatio"?: number;
}

export type com_vaonis_instruments_sdk_models_status_operations_StellinaObservationOperation_StellinaObservationAutofocusStepType = "LIVE" | "MANUAL_CONTINUE" | "MANUAL_RESTART" | "START_AUTO" | "START_FORCE" | "START_ON";

export interface com_vaonis_instruments_sdk_models_status_operations_StellinaObservationOperation_StellinaObservationParams {
  "algorithm"?: com_vaonis_instruments_sdk_models_status_operations_StellinaObservationOperation_StellinaPointingAlgorithm;
  "brightZoneOffset"?: com_vaonis_instruments_sdk_models_status_operations_StellinaObservationOperation_StellinaBrightZoneOffset;
  "cameraParams"?: com_vaonis_instruments_sdk_models_status_StellinaCapture_StellinaCameraParams;
  "hdrBackgroundParams"?: com_vaonis_instruments_sdk_models_status_operations_StellinaObservationOperation_StellinaHdrBackgroundParams;
  "stackingParams"?: com_vaonis_instruments_sdk_models_status_operations_StellinaObservationOperation_StellinaStackingParams;
}

export interface com_vaonis_instruments_sdk_models_status_operations_StellinaObservationOperation_StellinaObservationStep {
  "autofocusType"?: com_vaonis_instruments_sdk_models_status_operations_StellinaObservationOperation_StellinaObservationAutofocusStepType;
  "name"?: string;
  "progress"?: number;
  "steps"?: unknown[];
  "type"?: com_vaonis_instruments_sdk_models_status_operations_StellinaObservationOperation_StellinaObservationStepType;
}

export type com_vaonis_instruments_sdk_models_status_operations_StellinaObservationOperation_StellinaObservationStepType = "ASTROMETRY" | "AUTO_FOCUS" | "CAPTURE" | "CENTERING" | "GO_RELATIVE" | "GO_TARGET" | "LOOKING_FOR_SUN" | "POINTING_SUN" | "POINT_AT_OFFSET" | "POINT_AT_SECOND_OFFSET" | "POINT_BRIGHT_ZONE" | "POINT_DEEP_SKY" | "POINT_TARGET" | "SEEK_STOP_ALT" | "START_TRACKING" | "TRACKING" | "undefined";

export interface com_vaonis_instruments_sdk_models_status_operations_StellinaObservationOperation_StellinaObservationTarget {
  "coords"?: com_vaonis_instruments_sdk_models_status_StellinaSkyPosition;
  "objectId"?: string;
  "objectName"?: string;
  "objectType"?: string;
  "type"?: com_vaonis_instruments_sdk_models_status_operations_StellinaObservationOperation_ObservationTargetType;
}

export type com_vaonis_instruments_sdk_models_status_operations_StellinaObservationOperation_StellinaObservationType = "DEBUG_UI" | "MANUAL" | "PLAN" | "PLAYLIST" | "STANDARD" | "STORE" | "SUN";

export type com_vaonis_instruments_sdk_models_status_operations_StellinaObservationOperation_StellinaPointingAlgorithm = "AUTO" | "BRIGHT_ZONE" | "DEEP_SKY" | "DEEP_SKY_THEN_BRIGHT_ZONE";

export type com_vaonis_instruments_sdk_models_status_operations_StellinaObservationOperation_StellinaSolarObservationTarget = "jupiter" | "mars" | "mercury" | "moon" | "neptune" | "saturn" | "uranus" | "venus";

export interface com_vaonis_instruments_sdk_models_status_operations_StellinaObservationOperation_StellinaStackingParams {
  "backgroundEnabled"?: boolean;
  "backgroundPolyorder"?: number;
  "histogramEnabled"?: boolean;
  "histogramHigh"?: number;
  "histogramLow"?: number;
  "histogramMedium"?: number;
}

export interface com_vaonis_instruments_sdk_models_status_operations_StellinaObservationOperation_StellingCaptureStore {
  "state"?: com_vaonis_instruments_sdk_models_status_operations_StellinaObservationOperation_StellinaCaptureStoreState;
  "step"?: com_vaonis_instruments_sdk_models_status_operations_StellinaObservationOperation_StellingCaptureStore_Step;
  "storeId"?: string;
  "totalStackingCount"?: number;
}

export type com_vaonis_instruments_sdk_models_status_operations_StellinaObservationOperation_StellingCaptureStore_Step = "EXPORT_TIFF" | "SAVE_CGS";

export interface com_vaonis_instruments_sdk_models_status_operations_StellinaOpenOperation {
  "appVersion"?: string;
  "deviceId"?: string;
  "endTime"?: number;
  "error"?: com_vaonis_instruments_sdk_models_status_StellinaError;
  "id"?: string;
  "startTime"?: number;
  "stopped"?: boolean;
  "type"?: com_vaonis_instruments_sdk_models_status_operations_StellinaOperationType;
  "userId"?: number;
}

export type com_vaonis_instruments_sdk_models_status_operations_StellinaOperation = com_vaonis_instruments_sdk_models_status_operations_StellinaAutoInitOperation | com_vaonis_instruments_sdk_models_status_operations_StellinaDarkCalibrationOperation | com_vaonis_instruments_sdk_models_status_operations_StellinaDeleteFoldersOperation | com_vaonis_instruments_sdk_models_status_operations_StellinaObservationOperation | com_vaonis_instruments_sdk_models_status_operations_StellinaOpenOperation | com_vaonis_instruments_sdk_models_status_operations_StellinaParkOperation | com_vaonis_instruments_sdk_models_status_operations_StellinaPlanOperation | com_vaonis_instruments_sdk_models_status_operations_StellinaPlaylistOperation | com_vaonis_instruments_sdk_models_status_operations_StellinaStorageAcquisitionOperation | com_vaonis_instruments_sdk_models_status_operations_StellinaSunModeOperation;

export interface com_vaonis_instruments_sdk_models_status_operations_StellinaOperationMap {
  "autoInit"?: com_vaonis_instruments_sdk_models_status_operations_StellinaAutoInitOperation;
  "deleteFolders"?: com_vaonis_instruments_sdk_models_status_operations_StellinaDeleteFoldersOperation;
  "generateDark"?: com_vaonis_instruments_sdk_models_status_operations_StellinaDarkCalibrationOperation;
  "observation"?: com_vaonis_instruments_sdk_models_status_operations_StellinaObservationOperation;
  "open"?: com_vaonis_instruments_sdk_models_status_operations_StellinaOpenOperation;
  "park"?: com_vaonis_instruments_sdk_models_status_operations_StellinaParkOperation;
  "plan"?: com_vaonis_instruments_sdk_models_status_operations_StellinaPlanOperation;
  "playlist"?: com_vaonis_instruments_sdk_models_status_operations_StellinaPlaylistOperation;
  "storageAcquisition"?: com_vaonis_instruments_sdk_models_status_operations_StellinaStorageAcquisitionOperation;
  "sunMode"?: com_vaonis_instruments_sdk_models_status_operations_StellinaSunModeOperation;
}

export type com_vaonis_instruments_sdk_models_status_operations_StellinaOperationType = "AUTO_INIT" | "DELETE_FOLDERS" | "GENERATE_DARK" | "OBSERVATION" | "OPEN" | "PARK" | "PLAN" | "PLAYLIST" | "STORAGE_ACQUISITION" | "SUN_MODE" | "SUN_OBSERVATION";

export interface com_vaonis_instruments_sdk_models_status_operations_StellinaParkOperation {
  "appVersion"?: string;
  "deviceId"?: string;
  "endTime"?: number;
  "error"?: com_vaonis_instruments_sdk_models_status_StellinaError;
  "id"?: string;
  "startTime"?: number;
  "stopped"?: boolean;
  "type"?: com_vaonis_instruments_sdk_models_status_operations_StellinaOperationType;
  "userId"?: number;
}

export interface com_vaonis_instruments_sdk_models_status_operations_StellinaPlanOperation {
  "appVersion"?: string;
  "deviceId"?: string;
  "endTime"?: number;
  "error"?: com_vaonis_instruments_sdk_models_status_StellinaError;
  "id"?: string;
  "planId"?: string;
  "planName"?: string;
  "planVersion"?: string;
  "startTime"?: number;
  "state"?: com_vaonis_instruments_sdk_models_status_operations_StellinaPlanOperation_StellinaPlanOperationState;
  "stopped"?: boolean;
  "targets"?: com_vaonis_instruments_sdk_models_status_operations_StellinaPlanOperation_Target[];
  "type"?: com_vaonis_instruments_sdk_models_status_operations_StellinaOperationType;
  "userId"?: number;
}

export type com_vaonis_instruments_sdk_models_status_operations_StellinaPlanOperation_StellinaPlanOperationState = "AUTO_INIT" | "FINISHED" | "OBSERVATION" | "WAITING_FOR_OBSERVATION_START" | "WAITING_FOR_RETRY" | "WAITING_UNTIL_START";

export interface com_vaonis_instruments_sdk_models_status_operations_StellinaPlanOperation_Target {
  "attempts"?: com_vaonis_instruments_sdk_models_status_operations_StellinaPlanOperation_Target_Attempt[];
  "endTime"?: number;
  "mosaic"?: com_vaonis_instruments_sdk_models_body_mosaic_MosaicBody;
  "startTime"?: number;
  "storeId"?: string;
  "storeState"?: com_vaonis_instruments_sdk_models_status_operations_StellinaObservationOperation_StellinaCaptureStoreState;
  "target"?: com_vaonis_instruments_sdk_models_status_operations_StellinaObservationOperation_StellinaObservationTarget;
}

export interface com_vaonis_instruments_sdk_models_status_operations_StellinaPlanOperation_Target_Attempt {
  "endTime"?: number;
  "error"?: com_vaonis_instruments_sdk_models_status_StellinaError;
  "lastImage"?: com_vaonis_instruments_sdk_models_status_StellinaCapture_StellinaCaptureImage;
  "observationId"?: string;
  "stackingCount"?: number;
  "startTime"?: number;
  "stopped"?: boolean;
  "totalStackingCount"?: number;
}

export interface com_vaonis_instruments_sdk_models_status_operations_StellinaPlaylistOperation {
  "appVersion"?: string;
  "deviceId"?: string;
  "endTime"?: number;
  "error"?: com_vaonis_instruments_sdk_models_status_StellinaError;
  "id"?: string;
  "observations"?: com_vaonis_instruments_sdk_models_status_operations_StellinaPlaylistOperation_Observation[];
  "playlistType"?: com_vaonis_instruments_sdk_models_status_operations_StellinaPlaylistOperation_PlaylistType;
  "startTime"?: number;
  "stopped"?: boolean;
  "targets"?: unknown[];
  "type"?: com_vaonis_instruments_sdk_models_status_operations_StellinaOperationType;
  "userId"?: number;
}

export interface com_vaonis_instruments_sdk_models_status_operations_StellinaPlaylistOperation_Observation {
  "error"?: com_vaonis_instruments_sdk_models_status_StellinaError;
  "operationId"?: string;
  "succeeded"?: boolean;
}

export type com_vaonis_instruments_sdk_models_status_operations_StellinaPlaylistOperation_PlaylistType = "RANDOM";

export interface com_vaonis_instruments_sdk_models_status_operations_StellinaStorageAcquisitionOperation {
  "appVersion"?: string;
  "count"?: number;
  "deviceId"?: string;
  "endTime"?: number;
  "error"?: com_vaonis_instruments_sdk_models_status_StellinaError;
  "id"?: string;
  "path"?: string;
  "requiredCount"?: number;
  "startTime"?: number;
  "stopped"?: boolean;
  "type"?: com_vaonis_instruments_sdk_models_status_operations_StellinaOperationType;
  "userId"?: number;
}

export interface com_vaonis_instruments_sdk_models_status_operations_StellinaSunModeOperation {
  "appVersion"?: string;
  "deviceId"?: string;
  "eclipse"?: boolean;
  "endTime"?: number;
  "error"?: com_vaonis_instruments_sdk_models_status_StellinaError;
  "filterDetected"?: boolean;
  "filterDetectionSafetyTimeout"?: boolean;
  "id"?: string;
  "meanIndicatesFilterIsInstalled"?: boolean;
  "meanOverSafetyThreshold"?: boolean;
  "meanSafetyTimeout"?: boolean;
  "observationCount"?: number;
  "observationError"?: com_vaonis_instruments_sdk_models_status_StellinaError;
  "safetyEnabled"?: boolean;
  "startTime"?: number;
  "state"?: com_vaonis_instruments_sdk_models_status_operations_StellinaSunModeOperation_StellinaSunModeState;
  "stopped"?: boolean;
  "type"?: com_vaonis_instruments_sdk_models_status_operations_StellinaOperationType;
  "userId"?: number;
}

export type com_vaonis_instruments_sdk_models_status_operations_StellinaSunModeOperation_StellinaSunModePov = "earth" | "jupiter" | "mars" | "mercury" | "neptune" | "raw" | "saturn" | "uranus" | "venus";

export type com_vaonis_instruments_sdk_models_status_operations_StellinaSunModeOperation_StellinaSunModeState = "CLOSING_ARM" | "OBSERVATION" | "OPENING_ARM" | "WAITING_AFTER_OBSERVATION_FAILED" | "WAITING_FOR_FILTER_INSTALLATION" | "WAITING_FOR_FILTER_REMOVAL" | "WAITING_FOR_ORIENTATION";

export interface io_github_g00fy2_versioncompare_Version {
  "originalString"?: string;
  "preReleaseVersion"?: number;
  "releaseType"?: io_github_g00fy2_versioncompare_VersionComparator_ReleaseType;
  "subversionNumbers"?: unknown[];
  "suffix"?: string;
  "trimmedSubversionNumbers"?: unknown[];
}

export type io_github_g00fy2_versioncompare_VersionComparator_ReleaseType = "ALPHA" | "BETA" | "PRE_ALPHA" | "RC" | "SNAPSHOT" | "STABLE";

export interface SocketEventPayloads {
  "CONTROL_ERROR": unknown[];
  "STATUS_UPDATED": com_vaonis_instruments_sdk_models_status_StellinaStatus;
}

// Runtime exports from ./src/index.js
export const schemas: {
  $schema: string;
  title: string;
  events: Record<string, any>;
  definitions: Record<string, any>;
  meta?: any;
};

export const events: Record<string, any>;
export const definitions: Record<string, any>;

export function getEventSchema(eventName: string): any;
export function getDefinition(dotName: string): any;

