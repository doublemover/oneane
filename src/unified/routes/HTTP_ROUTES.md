# HTTP API Routes (Union: Stellina 2.35.7 + Vespera 3.0.12)

This file lists every HTTP route discovered from the firmware update bundles embedded in the Barnard Android app.

**Columns:** method, path, operationId (generated), models (where the route exists).

## /app

| Method | Path | OperationId | Models |
|---|---|---|---|
| POST | `/app/abortAllOperations` | `appPostAbortAllOperations` | stellina, vespera |
| POST | `/app/abortAllOperationsAndRestart` | `appPostAbortAllOperationsAndRestart` | stellina, vespera |
| POST | `/app/abortOperation` | `appPostAbortOperation` | stellina, vespera |
| POST | `/app/cleanInstrument` | `appPostCleanInstrument` | stellina, vespera |
| GET | `/app/debugStatus` | `appGetDebugStatus` | stellina, vespera |
| POST | `/app/debug_causeSegfault` | `appPostDebugCauseSegfault` | stellina, vespera |
| POST | `/app/debug_freeze` | `appPostDebugFreeze` | stellina, vespera |
| GET | `/app/getConfig` | `appGetGetConfig` | stellina, vespera |
| POST | `/app/setConfig` | `appPostSetConfig` | stellina, vespera |
| POST | `/app/setSettings` | `appPostSetSettings` | stellina, vespera |
| GET | `/app/status` | `appGetStatus` | stellina, vespera |

## /astrometry

| Method | Path | OperationId | Models |
|---|---|---|---|
| POST | `/astrometry/computeAstrometry` | `astrometryPostComputeAstrometry` | stellina, vespera |
| POST | `/astrometry/debug_convertImagePoint` | `astrometryPostDebugConvertImagePoint` | stellina, vespera |
| POST | `/astrometry/debug_setAstrometryResult` | `astrometryPostDebugSetAstrometryResult` | stellina, vespera |
| POST | `/astrometry/singleAstrometry` | `astrometryPostSingleAstrometry` | stellina, vespera |

## /automator

| Method | Path | OperationId | Models |
|---|---|---|---|
| POST | `/automator/findObservationTarget` | `automatorPostFindObservationTarget` | stellina, vespera |
| POST | `/automator/monitorTracking` | `automatorPostMonitorTracking` | stellina, vespera |
| POST | `/automator/processAstrometryFolders` | `automatorPostProcessAstrometryFolders` | stellina, vespera |
| POST | `/automator/processAutoFocusFolders` | `automatorPostProcessAutoFocusFolders` | stellina, vespera |
| POST | `/automator/runObservationProgram` | `automatorPostRunObservationProgram` | stellina, vespera |
| POST | `/automator/startHighConsomation` | `automatorPostStartHighConsomation` | stellina, vespera |
| POST | `/automator/startObservationProgram` | `automatorPostStartObservationProgram` | stellina, vespera |
| POST | `/automator/startTestingProgram` | `automatorPostStartTestingProgram` | stellina, vespera |
| POST | `/automator/takeSamples` | `automatorPostTakeSamples` | stellina, vespera |
| POST | `/automator/testAngularCorrection` | `automatorPostTestAngularCorrection` | stellina, vespera |
| POST | `/automator/testAngularCorrectionDerivation` | `automatorPostTestAngularCorrectionDerivation` | stellina, vespera |
| POST | `/automator/testAutoFocus` | `automatorPostTestAutoFocus` | stellina, vespera |
| POST | `/automator/testComputations` | `automatorPostTestComputations` | stellina, vespera |
| POST | `/automator/testMovements` | `automatorPostTestMovements` | stellina, vespera |
| POST | `/automator/testPointing` | `automatorPostTestPointing` | stellina, vespera |
| POST | `/automator/testPointingWithAstrometry` | `automatorPostTestPointingWithAstrometry` | stellina, vespera |
| POST | `/automator/testTracking` | `automatorPostTestTracking` | stellina, vespera |
| POST | `/automator/writeMosaicProgram` | `automatorPostWriteMosaicProgram` | stellina, vespera |

## /battery

| Method | Path | OperationId | Models |
|---|---|---|---|
| POST | `/battery/cancelAssociation` | `batteryPostCancelAssociation` | stellina, vespera |
| POST | `/battery/proposeAssociation` | `batteryPostProposeAssociation` | stellina, vespera |

## /board

| Method | Path | OperationId | Models |
|---|---|---|---|
| POST | `/board/causeCrash` | `boardPostCauseCrash__board_causeCrash` | vespera |
| POST | `/board/causeFreeze` | `boardPostCauseFreeze__board_causeFreeze` | vespera |
| POST | `/board/cause_crash` | `boardPostCauseCrash__board_cause_crash` | stellina |
| POST | `/board/cause_freeze` | `boardPostCauseFreeze__board_cause_freeze` | stellina |
| POST | `/board/debug_failOnNextFrame` | `boardPostDebugFailOnNextFrame` | stellina, vespera |
| POST | `/board/debug_pollRegister` | `boardPostDebugPollRegister` | stellina, vespera |
| POST | `/board/debug_readTime` | `boardPostDebugReadTime` | stellina, vespera |
| POST | `/board/debug_testTime` | `boardPostDebugTestTime` | stellina, vespera |
| POST | `/board/flash` | `boardPostFlash` | stellina, vespera |
| POST | `/board/forceState` | `boardPostForceState` | vespera |
| POST | `/board/position` | `boardPostPosition` | stellina, vespera |
| POST | `/board/ready` | `boardPostReady` | stellina, vespera |
| POST | `/board/ref` | `boardPostRef` | stellina, vespera |
| POST | `/board/refreshRef` | `boardPostRefreshRef` | stellina, vespera |
| POST | `/board/requestShutdown` | `boardPostRequestShutdown` | stellina, vespera |
| POST | `/board/reset` | `boardPostReset` | stellina, vespera |
| POST | `/board/sendFrame` | `boardPostSendFrame` | stellina, vespera |
| POST | `/board/sim_powerButtonPush` | `boardPostSimPowerButtonPush` | stellina, vespera |
| POST | `/board/target` | `boardPostTarget` | stellina, vespera |
| POST | `/board/time` | `boardPostTime` | stellina, vespera |

## /boardDebug

| Method | Path | OperationId | Models |
|---|---|---|---|
| POST | `/boardDebug/goHome` | `boardDebugPostGoHome` | stellina, vespera |
| POST | `/boardDebug/sendCommand` | `boardDebugPostSendCommand` | stellina, vespera |
| POST | `/boardDebug/testButton` | `boardDebugPostTestButton` | stellina, vespera |
| POST | `/boardDebug/testCamera` | `boardDebugPostTestCamera` | stellina, vespera |
| POST | `/boardDebug/testSens` | `boardDebugPostTestSens` | stellina, vespera |
| POST | `/boardDebug/testTorque` | `boardDebugPostTestTorque` | stellina, vespera |
| GET | `/boardDebug/torqueChart` | `boardDebugGetTorqueChart` | stellina, vespera |
| GET | `/boardDebug/torqueCsv` | `boardDebugGetTorqueCsv` | stellina, vespera |

## /camera

| Method | Path | OperationId | Models |
|---|---|---|---|
| POST | `/camera/changeSunPov` | `cameraPostChangeSunPov` | stellina, vespera |
| POST | `/camera/debug_readParams` | `cameraPostDebugReadParams` | stellina, vespera |
| POST | `/camera/debug_stressTest` | `cameraPostDebugStressTest` | stellina, vespera |
| POST | `/camera/pauseAcquisition` | `cameraPostPauseAcquisition` | stellina, vespera |
| POST | `/camera/restartAcquisition` | `cameraPostRestartAcquisition` | stellina, vespera |
| POST | `/camera/resumeAcquisition` | `cameraPostResumeAcquisition` | stellina, vespera |
| POST | `/camera/setAcquisitionFolder2` | `cameraPostSetAcquisitionFolder2` | stellina, vespera |
| POST | `/camera/singleAcquisition` | `cameraPostSingleAcquisition` | stellina, vespera |
| POST | `/camera/startAcquisition` | `cameraPostStartAcquisition` | stellina, vespera |
| POST | `/camera/updateAcquisitionExposure` | `cameraPostUpdateAcquisitionExposure` | stellina, vespera |
| POST | `/camera/updateAcquisitionExposureMode` | `cameraPostUpdateAcquisitionExposureMode` | stellina, vespera |
| POST | `/camera/updateAcquisitionGain` | `cameraPostUpdateAcquisitionGain` | stellina, vespera |

## /capture

| Method | Path | OperationId | Models |
|---|---|---|---|
| POST | `/capture/exportImageHdr` | `capturePostExportImageHdr` | stellina, vespera |
| POST | `/capture/exportImageTiff` | `capturePostExportImageTiff` | stellina, vespera |
| POST | `/capture/setToBeResumable` | `capturePostSetToBeResumable` | stellina, vespera |
| POST | `/capture/startCapture` | `capturePostStartCapture` | stellina, vespera |
| POST | `/capture/stopCapture` | `capturePostStopCapture` | stellina, vespera |

## /captureStore

| Method | Path | OperationId | Models |
|---|---|---|---|
| POST | `/captureStore/deleteAllStoredCaptures` | `captureStorePostDeleteAllStoredCaptures` | stellina, vespera |
| POST | `/captureStore/deleteStoredCapture` | `captureStorePostDeleteStoredCapture` | stellina, vespera |
| GET | `/captureStore/getObservation` | `captureStoreGetGetObservation` | stellina, vespera |
| POST | `/captureStore/startObservationFromStoredCapture` | `captureStorePostStartObservationFromStoredCapture` | stellina, vespera |

## /darkManager

| Method | Path | OperationId | Models |
|---|---|---|---|
| POST | `/darkManager/deleteDark` | `darkManagerPostDeleteDark` | stellina, vespera |
| POST | `/darkManager/generateDark` | `darkManagerPostGenerateDark` | stellina, vespera |
| POST | `/darkManager/stopGenerateDark` | `darkManagerPostStopGenerateDark` | stellina, vespera |

## /debug

| Method | Path | OperationId | Models |
|---|---|---|---|
| POST | `/debug/copyFile` | `debugPostCopyFile` | stellina, vespera |
| POST | `/debug/motors/fakeCalibration` | `debugPostFakeCalibration` | stellina, vespera |
| POST | `/debug/motors/readAllStatusRegisters` | `debugPostReadAllStatusRegisters` | stellina, vespera |

## /expertMode

| Method | Path | OperationId | Models |
|---|---|---|---|
| POST | `/expertMode/startStorageAcquisition` | `expertModePostStartStorageAcquisition` | stellina, vespera |
| POST | `/expertMode/stopStorageAcquisition` | `expertModePostStopStorageAcquisition` | stellina, vespera |

## /externalProcess

| Method | Path | OperationId | Models |
|---|---|---|---|
| POST | `/externalProcess/debug_setSimSettings` | `externalProcessPostDebugSetSimSettings` | stellina, vespera |

## /focus

| Method | Path | OperationId | Models |
|---|---|---|---|
| POST | `/focus/clearHistory` | `focusPostClearHistory` | stellina, vespera |
| POST | `/focus/computeFocusValue` | `focusPostComputeFocusValue` | stellina, vespera |
| POST | `/focus/computeInitialSequence` | `focusPostComputeInitialSequence` | stellina, vespera |
| POST | `/focus/debug_setFocusValueResult` | `focusPostDebugSetFocusValueResult` | stellina, vespera |
| POST | `/focus/processCurrentHistory` | `focusPostProcessCurrentHistory` | stellina, vespera |
| POST | `/focus/processHistory` | `focusPostProcessHistory` | stellina, vespera |
| POST | `/focus/singleFocus` | `focusPostSingleFocus` | stellina, vespera |
| POST | `/focus/startAutoFocus` | `focusPostStartAutoFocus` | stellina, vespera |

## /general

| Method | Path | OperationId | Models |
|---|---|---|---|
| POST | `/general/adjustObservationFocus` | `generalPostAdjustObservationFocus` | stellina, vespera |
| POST | `/general/adjustObservationFraming` | `generalPostAdjustObservationFraming` | stellina, vespera |
| POST | `/general/debug_fakeAutoInit` | `generalPostDebugFakeAutoInit` | stellina, vespera |
| POST | `/general/openForMaintenance` | `generalPostOpenForMaintenance` | stellina, vespera |
| POST | `/general/park` | `generalPostPark` | stellina, vespera |
| POST | `/general/pointBrightZone` | `generalPostPointBrightZone` | stellina, vespera |
| POST | `/general/pointDeepSky` | `generalPostPointDeepSky` | stellina, vespera |
| POST | `/general/startAutoInit` | `generalPostStartAutoInit` | stellina, vespera |
| POST | `/general/startManualInit` | `generalPostStartManualInit` | stellina, vespera |
| POST | `/general/startObservation` | `generalPostStartObservation` | stellina, vespera |
| POST | `/general/startObservationCapture` | `generalPostStartObservationCapture` | stellina, vespera |
| POST | `/general/startObservationPointing` | `generalPostStartObservationPointing` | stellina, vespera |
| POST | `/general/stopAutoInit` | `generalPostStopAutoInit` | stellina, vespera |
| POST | `/general/stopObservation` | `generalPostStopObservation` | stellina, vespera |
| POST | `/general/stopObservationCapture` | `generalPostStopObservationCapture` | stellina, vespera |
| POST | `/general/stopObservationPointing` | `generalPostStopObservationPointing` | stellina, vespera |

## /internalBattery

| Method | Path | OperationId | Models |
|---|---|---|---|
| POST | `/internalBattery/debug_setFakeBatteryLevel` | `internalBatteryPostDebugSetFakeBatteryLevel` | stellina, vespera |

## /leds

| Method | Path | OperationId | Models |
|---|---|---|---|
| POST | `/leds/setColor` | `ledsPostSetColor` | vespera |
| POST | `/leds/setIntensity` | `ledsPostSetIntensity` | vespera |

## /logs

| Method | Path | OperationId | Models |
|---|---|---|---|
| POST | `/logs/consume` | `logsPostConsume` | stellina, vespera |
| POST | `/logs/debug_fakeState` | `logsPostDebugFakeState` | stellina, vespera |

## /misc

| Method | Path | OperationId | Models |
|---|---|---|---|
| POST | `/misc/setTimeForSunAlt` | `miscPostSetTimeForSunAlt` | stellina, vespera |

## /motors

| Method | Path | OperationId | Models |
|---|---|---|---|
| POST | `/motors/applyAngularCorrection` | `motorsPostApplyAngularCorrection` | stellina, vespera |
| POST | `/motors/applyReframeCorrection` | `motorsPostApplyReframeCorrection` | stellina, vespera |
| POST | `/motors/defineZenithAngleForDer0FromAcquisition` | `motorsPostDefineZenithAngleForDer0FromAcquisition` | stellina, vespera |
| POST | `/motors/getPlay` | `motorsPostGetPlay` | stellina, vespera |
| POST | `/motors/goAbsolute` | `motorsPostGoAbsolute` | stellina, vespera |
| POST | `/motors/goRelative` | `motorsPostGoRelative` | stellina, vespera |
| POST | `/motors/goTarget` | `motorsPostGoTarget` | stellina, vespera |
| POST | `/motors/pointTarget` | `motorsPostPointTarget` | stellina, vespera |
| POST | `/motors/pointTargetWithPixelOffset` | `motorsPostPointTargetWithPixelOffset` | stellina, vespera |
| POST | `/motors/putZenithUp` | `motorsPostPutZenithUp` | stellina, vespera |
| POST | `/motors/saveZenithAngleForDer0` | `motorsPostSaveZenithAngleForDer0` | stellina, vespera |
| POST | `/motors/seekStop` | `motorsPostSeekStop` | stellina, vespera |
| POST | `/motors/setFactoryFocus` | `motorsPostSetFactoryFocus` | stellina, vespera |
| POST | `/motors/setPlay` | `motorsPostSetPlay` | stellina, vespera |
| POST | `/motors/stop` | `motorsPostStop` | stellina, vespera |
| POST | `/motors/track` | `motorsPostTrack` | stellina, vespera |

## /network

| Method | Path | OperationId | Models |
|---|---|---|---|
| POST | `/network/certif` | `networkPostCertif` | stellina, vespera |
| POST | `/network/disableNetworkInterface` | `networkPostDisableNetworkInterface` | stellina, vespera |
| POST | `/network/getInterfaceStatus` | `networkPostGetInterfaceStatus` | stellina, vespera |
| POST | `/network/selectChannel` | `networkPostSelectChannel` | stellina, vespera |
| POST | `/network/switchFrequency` | `networkPostSwitchFrequency` | stellina, vespera |

## /planner

| Method | Path | OperationId | Models |
|---|---|---|---|
| POST | `/planner/clearPreviousPlanOperation` | `plannerPostClearPreviousPlanOperation` | stellina, vespera |
| GET | `/planner/getPlanObservation` | `plannerGetGetPlanObservation` | stellina, vespera |
| POST | `/planner/startPlan` | `plannerPostStartPlan` | stellina, vespera |
| POST | `/planner/stopPlan` | `plannerPostStopPlan` | stellina, vespera |

## /playlist

| Method | Path | OperationId | Models |
|---|---|---|---|
| POST | `/playlist/startPlaylist` | `playlistPostStartPlaylist` | stellina, vespera |
| POST | `/playlist/stopPlaylist` | `playlistPostStopPlaylist` | stellina, vespera |

## /region

| Method | Path | OperationId | Models |
|---|---|---|---|
| POST | `/region/setCountryCode` | `regionPostSetCountryCode` | stellina, vespera |

## /reporter

| Method | Path | OperationId | Models |
|---|---|---|---|
| GET | `/reporter/getAvailableReports` | `reporterGetGetAvailableReports` | stellina, vespera |
| POST | `/reporter/markReportsAsSynced` | `reporterPostMarkReportsAsSynced` | stellina, vespera |

## /sensors

| Method | Path | OperationId | Models |
|---|---|---|---|
| POST | `/sensors/debug_setFilter` | `sensorsPostDebugSetFilter` | stellina, vespera |
| POST | `/sensors/debug_setSensor` | `sensorsPostDebugSetSensor` | stellina, vespera |
| POST | `/sensors/debug_setTemperature` | `sensorsPostDebugSetTemperature` | stellina, vespera |
| POST | `/sensors/read` | `sensorsPostRead` | stellina, vespera |
| POST | `/sensors/setDefogMode` | `sensorsPostSetDefogMode` | stellina, vespera |

## /sequence

| Method | Path | OperationId | Models |
|---|---|---|---|
| POST | `/sequence/armOrientation` | `sequencePostArmOrientation` | stellina, vespera |
| POST | `/sequence/startSequence` | `sequencePostStartSequence` | stellina, vespera |
| POST | `/sequence/stopSequence` | `sequencePostStopSequence` | stellina, vespera |

## /socket

| Method | Path | OperationId | Models |
|---|---|---|---|
| POST | `/socket/debug_setMasterDeviceId` | `socketPostDebugSetMasterDeviceId` | stellina, vespera |

## /stacking

| Method | Path | OperationId | Models |
|---|---|---|---|
| POST | `/stacking/liveStackFolder` | `stackingPostLiveStackFolder` | stellina, vespera |
| POST | `/stacking/processLiveRegistrationResult` | `stackingPostProcessLiveRegistrationResult` | stellina, vespera |

## /stellarium

| Method | Path | OperationId | Models |
|---|---|---|---|
| POST | `/stellarium/setOffsets` | `stellariumPostSetOffsets` | stellina, vespera |

## /storage

| Method | Path | OperationId | Models |
|---|---|---|---|
| POST | `/storage/clearRamDisk` | `storagePostClearRamDisk` | stellina, vespera |
| GET | `/storage/content` | `storageGetContent` | stellina, vespera |
| POST | `/storage/deleteUserStorageFolders` | `storagePostDeleteUserStorageFolders` | stellina, vespera |
| POST | `/storage/sim_setStorageSizeAvailable` | `storagePostSimSetStorageSizeAvailable` | stellina, vespera |
| GET | `/storage/userStorageFolderContent` | `storageGetUserStorageFolderContent` | stellina, vespera |

## /sun

| Method | Path | OperationId | Models |
|---|---|---|---|
| POST | `/sun/applyManualGuidingCorrection` | `sunPostApplyManualGuidingCorrection` | stellina, vespera |
| POST | `/sun/changePov` | `sunPostChangePov` | stellina, vespera |
| POST | `/sun/debug_simShortcut` | `sunPostDebugSimShortcut` | stellina, vespera |
| POST | `/sun/disableGuidingCorrections` | `sunPostDisableGuidingCorrections` | stellina, vespera |
| POST | `/sun/enableGuidingCorrections` | `sunPostEnableGuidingCorrections` | stellina, vespera |
| POST | `/sun/handleUserAction` | `sunPostHandleUserAction` | stellina, vespera |
| POST | `/sun/pointSun` | `sunPostPointSun` | stellina, vespera |
| POST | `/sun/restartAutofocus` | `sunPostRestartAutofocus` | stellina, vespera |
| POST | `/sun/restartCapture` | `sunPostRestartCapture` | stellina, vespera |
| POST | `/sun/setUserParams` | `sunPostSetUserParams` | stellina, vespera |
| POST | `/sun/startSunMode` | `sunPostStartSunMode` | stellina, vespera |
| POST | `/sun/stopObservation` | `sunPostStopObservation` | stellina, vespera |
| POST | `/sun/stopSunMode` | `sunPostStopSunMode` | stellina, vespera |
| POST | `/sun/sunManuallyDetected` | `sunPostSunManuallyDetected` | stellina, vespera |

## /test

| Method | Path | OperationId | Models |
|---|---|---|---|
| GET | `/test` | `testGetTest` | stellina, vespera |
| GET | `/test/sink` | `testGetSink` | stellina, vespera |
| GET | `/test/sink-no-timeout` | `testGetSinkNoTimeout` | stellina, vespera |
| GET | `/test/sink-timeout` | `testGetSinkTimeout` | stellina, vespera |

## /updates

| Method | Path | OperationId | Models |
|---|---|---|---|
| POST | `/updates/clearUpdateFolder` | `updatesPostClearUpdateFolder` | stellina, vespera |
| POST | `/updates/installUpdate` | `updatesPostInstallUpdate` | stellina, vespera |
| POST | `/updates/uploadUpdateFile` | `updatesPostUploadUpdateFile` | stellina, vespera |
