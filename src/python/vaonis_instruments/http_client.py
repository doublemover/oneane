"""HTTP client for the Vaonis instrument API (as used by com.vaonis.barnard).

This file is auto-generated from static analysis of the Android app.

Notes:
- Base URL is typically http://10.0.0.1:8082/v1 when connected to the telescope Wi-Fi.
- Many control endpoints require a custom Authorization header (see docs).
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import logging
import time
from typing import Any, Dict, Optional

import requests

from .logging_utils import format_payload


def _looks_like_image(data: bytes, content_type: Optional[str]) -> bool:
    if content_type and content_type.lower().startswith("image/"):
        return True
    if len(data) < 4:
        return False
    if data[:3] == b"\xff\xd8\xff":
        return True  # JPEG
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return True  # PNG
    if data[:2] == b"BM":
        return True  # BMP
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return True  # GIF
    if data[:4] in (b"II*\x00", b"MM\x00*"):
        return True  # TIFF
    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return True  # WEBP
    return False


def _summarize_files(files: Any) -> Optional[Dict[str, str]]:
    if files is None:
        return None
    if isinstance(files, dict):
        summary: Dict[str, str] = {}
        for key, value in files.items():
            if hasattr(value, "name"):
                summary[key] = str(getattr(value, "name"))
            elif isinstance(value, tuple) and value:
                summary[key] = str(value[0])
            else:
                summary[key] = type(value).__name__
        return summary
    return {"files": type(files).__name__}


@dataclass
class VaonisHTTPClient:
    """Minimal HTTP client.

    Parameters
    ----------
    base_url:
        Example: "http://10.0.0.1:8082/v1"
    timeout_s:
        Requests timeout in seconds.
    """

    base_url: str = "http://10.0.0.1:8082/v1"
    timeout_s: float = 10.0
    logger: Optional[logging.Logger] = None
    log_payloads: bool = True
    log_payload_limit: int = 4000

    def _log(self, message: str, *args: Any) -> None:
        if self.logger is not None:
            self.logger.info(message, *args)

    def _request(
        self,
        method: str,
        path: str,
        *,
        auth: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        json_body: Any = None,
        files: Any = None,
        stream: bool = False,
    ) -> requests.Response:
        url = self.base_url.rstrip("/") + "/" + path.lstrip("/")
        headers: Dict[str, str] = {}
        if auth is not None:
            headers["Authorization"] = auth
        body_repr: Optional[str] = None
        if json_body is not None:
            try:
                body_repr = json.dumps(json_body, ensure_ascii=True)
            except TypeError:
                body_repr = str(json_body)
        files_repr = _summarize_files(files)
        self._log(
            "HTTP request %s %s params=%s json=%s files=%s",
            method,
            url,
            params,
            body_repr,
            files_repr,
        )
        start = time.monotonic()
        try:
            resp = requests.request(
                method,
                url,
                params=params,
                json=json_body,
                files=files,
                headers=headers,
                timeout=self.timeout_s,
                stream=stream,
            )
        except requests.RequestException as exc:
            if self.logger is not None:
                self.logger.exception("HTTP error %s %s: %s", method, url, exc)
            raise
        elapsed_ms = (time.monotonic() - start) * 1000.0
        size: Optional[int]
        if stream:
            size = None
        else:
            try:
                size = len(resp.content)
            except Exception:
                size = None
        self._log(
            "HTTP response %s %s status=%s elapsed_ms=%.1f bytes=%s",
            method,
            url,
            resp.status_code,
            elapsed_ms,
            size,
        )
        if self.logger is not None and self.log_payloads and not stream:
            content_type = resp.headers.get("content-type", "")
            if (
                content_type.startswith("image/")
                or "application/octet-stream" in content_type
            ):
                payload = f"<{len(resp.content)} bytes>"
            else:
                payload = format_payload(
                    resp.text, color=False, max_len=self.log_payload_limit
                )
            self._log("HTTP response body %s %s payload=%s", method, url, payload)
        resp.raise_for_status()
        return resp

    def adjust_observation_focus(self, auth: str, body: Any) -> Any:
        """POST /v1/general/adjustObservationFocus
        Requires: Authorization header
        JSON body: Lcom/vaonis/instruments/sdk/models/body/AdjustFocusBody;
        Return (Android/Kotlin signature): (Ljava/lang/String;Lcom/vaonis/instruments/sdk/models/body/AdjustFocusBody;Lkotlin/coroutines/Continuation<-Lcom/vaonis/instruments/sdk/models/response/OrderResponse;>;)Ljava/lang/Object;
        """
        params = None
        resp = self._request(
            "POST",
            "general/adjustObservationFocus",
            auth=auth,
            params=params,
            json_body=body,
            files=None,
        )
        # Most endpoints return JSON
        try:
            return resp.json()
        except ValueError:
            return resp.text

    def adjust_observation_framing(self, auth: str, body: Any) -> Any:
        """POST /v1/general/adjustObservationFraming
        Requires: Authorization header
        JSON body: Lcom/vaonis/instruments/sdk/models/body/AdjustFramingBody;
        Return (Android/Kotlin signature): (Ljava/lang/String;Lcom/vaonis/instruments/sdk/models/body/AdjustFramingBody;Lkotlin/coroutines/Continuation<-Lcom/vaonis/instruments/sdk/models/response/OrderResponse;>;)Ljava/lang/Object;
        """
        params = None
        resp = self._request(
            "POST",
            "general/adjustObservationFraming",
            auth=auth,
            params=params,
            json_body=body,
            files=None,
        )
        # Most endpoints return JSON
        try:
            return resp.json()
        except ValueError:
            return resp.text

    def apply_reset_code(self, auth: str, body: Any) -> Any:
        """POST /v1/userManager/applyResetResponse
        Requires: Authorization header
        JSON body: Lcom/vaonis/instruments/sdk/models/body/RequestCodeBody;
        Return (Android/Kotlin signature): (Ljava/lang/String;Lcom/vaonis/instruments/sdk/models/body/RequestCodeBody;Lkotlin/coroutines/Continuation<-Lcom/vaonis/instruments/sdk/models/response/OrderResponse;>;)Ljava/lang/Object;
        """
        params = None
        resp = self._request(
            "POST",
            "userManager/applyResetResponse",
            auth=auth,
            params=params,
            json_body=body,
            files=None,
        )
        # Most endpoints return JSON
        try:
            return resp.json()
        except ValueError:
            return resp.text

    def change_pov(self, auth: str, body: Any) -> Any:
        """POST /v1/sun/changePov
        Requires: Authorization header
        JSON body: Lcom/vaonis/instruments/sdk/models/body/SunModePovBody;
        Return (Android/Kotlin signature): (Ljava/lang/String;Lcom/vaonis/instruments/sdk/models/body/SunModePovBody;Lkotlin/coroutines/Continuation<-Lcom/vaonis/instruments/sdk/models/response/OrderResponse;>;)Ljava/lang/Object;
        """
        params = None
        resp = self._request(
            "POST",
            "sun/changePov",
            auth=auth,
            params=params,
            json_body=body,
            files=None,
        )
        # Most endpoints return JSON
        try:
            return resp.json()
        except ValueError:
            return resp.text

    def consume_logs(self, auth: str) -> Any:
        """POST /v1/logs/consume
        Requires: Authorization header
        Return (Android/Kotlin signature): (Ljava/lang/String;Lkotlin/coroutines/Continuation<-Lcom/vaonis/instruments/sdk/models/response/LogResponse;>;)Ljava/lang/Object;
        """
        params = None
        resp = self._request(
            "POST", "logs/consume", auth=auth, params=params, json_body=None, files=None
        )
        # Most endpoints return JSON
        try:
            return resp.json()
        except ValueError:
            return resp.text

    def delete_stored_capture(self, auth: str, body: Any) -> Any:
        """POST /v1/captureStore/deleteStoredCapture
        Requires: Authorization header
        JSON body: Lcom/vaonis/instruments/sdk/models/body/DeleteStoredCaptureBody;
        Return (Android/Kotlin signature): (Ljava/lang/String;Lcom/vaonis/instruments/sdk/models/body/DeleteStoredCaptureBody;Lkotlin/coroutines/Continuation<-Lcom/vaonis/instruments/sdk/models/response/OrderResponse;>;)Ljava/lang/Object;
        """
        params = None
        resp = self._request(
            "POST",
            "captureStore/deleteStoredCapture",
            auth=auth,
            params=params,
            json_body=body,
            files=None,
        )
        # Most endpoints return JSON
        try:
            return resp.json()
        except ValueError:
            return resp.text

    def delete_user_storage_folder(self, auth: str, body: Any) -> Any:
        """POST /v1/storage/deleteUserStorageFolders
        Requires: Authorization header
        JSON body: Lcom/vaonis/instruments/sdk/models/body/DeleteUserStorageFolderBody;
        Return (Android/Kotlin signature): (Ljava/lang/String;Lcom/vaonis/instruments/sdk/models/body/DeleteUserStorageFolderBody;Lkotlin/coroutines/Continuation<-Lcom/vaonis/instruments/sdk/models/response/OrderResponse;>;)Ljava/lang/Object;
        """
        params = None
        resp = self._request(
            "POST",
            "storage/deleteUserStorageFolders",
            auth=auth,
            params=params,
            json_body=body,
            files=None,
        )
        # Most endpoints return JSON
        try:
            return resp.json()
        except ValueError:
            return resp.text

    def export_tiff(self, auth: str, body: Any) -> Any:
        """POST /v1/capture/exportImageTiff
        Requires: Authorization header
        JSON body: Lcom/vaonis/instruments/sdk/models/body/TiffBody;
        Return (Android/Kotlin signature): (Ljava/lang/String;Lcom/vaonis/instruments/sdk/models/body/TiffBody;Lkotlin/coroutines/Continuation<-Lcom/vaonis/instruments/sdk/models/response/TiffResponse;>;)Ljava/lang/Object;
        """
        params = None
        resp = self._request(
            "POST",
            "capture/exportImageTiff",
            auth=auth,
            params=params,
            json_body=body,
            files=None,
        )
        # Most endpoints return JSON
        try:
            return resp.json()
        except ValueError:
            return resp.text

    def generate_dark(self, auth: str) -> Any:
        """POST /v1/darkManager/generateDark
        Requires: Authorization header
        Return (Android/Kotlin signature): (Ljava/lang/String;Lkotlin/coroutines/Continuation<-Lcom/vaonis/instruments/sdk/models/response/OrderResponse;>;)Ljava/lang/Object;
        """
        params = None
        resp = self._request(
            "POST",
            "darkManager/generateDark",
            auth=auth,
            params=params,
            json_body=None,
            files=None,
        )
        # Most endpoints return JSON
        try:
            return resp.json()
        except ValueError:
            return resp.text

    def get_available_report(self) -> Any:
        """GET /v1/reporter/getAvailableReports
        Return (Android/Kotlin signature): (Lkotlin/coroutines/Continuation<-Lcom/vaonis/instruments/sdk/models/response/ReportsResponse;>;)Ljava/lang/Object;
        """
        params = None
        resp = self._request(
            "GET",
            "reporter/getAvailableReports",
            auth=None,
            params=params,
            json_body=None,
            files=None,
        )
        # Most endpoints return JSON
        try:
            return resp.json()
        except ValueError:
            return resp.text

    def get_plan_observation(self, observation_id: Any) -> Any:
        """GET /v1/planner/getPlanObservation
        Query params: observationId
        Return (Android/Kotlin signature): (Ljava/lang/String;Lkotlin/coroutines/Continuation<-Lcom/vaonis/instruments/sdk/models/response/PlanObservationResponse;>;)Ljava/lang/Object;
        """
        params: Dict[str, Any] = {}
        params["observationId"] = observation_id
        resp = self._request(
            "GET",
            "planner/getPlanObservation",
            auth=None,
            params=params,
            json_body=None,
            files=None,
        )
        # Most endpoints return JSON
        try:
            return resp.json()
        except ValueError:
            return resp.text

    def get_status(self) -> Any:
        """GET /v1/app/status
        Return (Android/Kotlin signature): (Lkotlin/coroutines/Continuation<-Lcom/vaonis/instruments/sdk/models/response/StatusResponse;>;)Ljava/lang/Object;
        """
        params = None
        resp = self._request(
            "GET", "app/status", auth=None, params=params, json_body=None, files=None
        )
        # Most endpoints return JSON
        try:
            return resp.json()
        except ValueError:
            return resp.text

    def get_storage_folder_content(self, folder_path: Any) -> Any:
        """GET /v1/storage/userStorageFolderContent
        Query params: folderPath
        Return (Android/Kotlin signature): (Ljava/lang/String;Lkotlin/coroutines/Continuation<-Lcom/vaonis/instruments/sdk/models/response/FolderContentResponse;>;)Ljava/lang/Object;
        """
        params: Dict[str, Any] = {}
        params["folderPath"] = folder_path
        resp = self._request(
            "GET",
            "storage/userStorageFolderContent",
            auth=None,
            params=params,
            json_body=None,
            files=None,
        )
        # Most endpoints return JSON
        try:
            return resp.json()
        except ValueError:
            return resp.text

    def get_stored_capture_observation(self, store_id: Any) -> Any:
        """GET /v1/captureStore/getObservation
        Query params: storeId
        Return (Android/Kotlin signature): (Ljava/lang/String;Lkotlin/coroutines/Continuation<-Lcom/vaonis/instruments/sdk/models/response/StoredObservationResponse;>;)Ljava/lang/Object;
        """
        params: Dict[str, Any] = {}
        params["storeId"] = store_id
        resp = self._request(
            "GET",
            "captureStore/getObservation",
            auth=None,
            params=params,
            json_body=None,
            files=None,
        )
        # Most endpoints return JSON
        try:
            return resp.json()
        except ValueError:
            return resp.text

    def mark_reports_as_synced(self, auth: str, body: Any) -> Any:
        """POST /v1/reporter/markReportsAsSynced
        Requires: Authorization header
        JSON body: Lcom/vaonis/instruments/sdk/models/body/ReportsBody;
        Return (Android/Kotlin signature): (Ljava/lang/String;Lcom/vaonis/instruments/sdk/models/body/ReportsBody;Lkotlin/coroutines/Continuation<-Lkotlin/Unit;>;)Ljava/lang/Object;
        """
        params = None
        resp = self._request(
            "POST",
            "reporter/markReportsAsSynced",
            auth=auth,
            params=params,
            json_body=body,
            files=None,
        )
        # Most endpoints return JSON
        try:
            return resp.json()
        except ValueError:
            return resp.text

    def open_arm(self, auth: str) -> Any:
        """POST /v1/general/openForMaintenance
        Requires: Authorization header
        Return (Android/Kotlin signature): (Ljava/lang/String;Lkotlin/coroutines/Continuation<-Lcom/vaonis/instruments/sdk/models/response/OrderResponse;>;)Ljava/lang/Object;
        """
        params = None
        resp = self._request(
            "POST",
            "general/openForMaintenance",
            auth=auth,
            params=params,
            json_body=None,
            files=None,
        )
        # Most endpoints return JSON
        try:
            return resp.json()
        except ValueError:
            return resp.text

    def park_arm(self, auth: str) -> Any:
        """POST /v1/general/park
        Requires: Authorization header
        Return (Android/Kotlin signature): (Ljava/lang/String;Lkotlin/coroutines/Continuation<-Lcom/vaonis/instruments/sdk/models/response/OrderResponse;>;)Ljava/lang/Object;
        """
        params = None
        resp = self._request(
            "POST", "general/park", auth=auth, params=params, json_body=None, files=None
        )
        # Most endpoints return JSON
        try:
            return resp.json()
        except ValueError:
            return resp.text

    def request_reset_code(self, auth: str) -> Any:
        """POST /v1/userManager/makeResetRequest
        Requires: Authorization header
        Return (Android/Kotlin signature): (Ljava/lang/String;Lkotlin/coroutines/Continuation<-Lcom/vaonis/instruments/sdk/models/response/ResetCodeResponse;>;)Ljava/lang/Object;
        """
        params = None
        resp = self._request(
            "POST",
            "userManager/makeResetRequest",
            auth=auth,
            params=params,
            json_body=None,
            files=None,
        )
        # Most endpoints return JSON
        try:
            return resp.json()
        except ValueError:
            return resp.text

    def request_shutdown(self, auth: str) -> Any:
        """POST /v1/board/requestShutdown
        Requires: Authorization header
        Return (Android/Kotlin signature): (Ljava/lang/String;Lkotlin/coroutines/Continuation<-Lcom/vaonis/instruments/sdk/models/response/OrderResponse;>;)Ljava/lang/Object;
        """
        params = None
        resp = self._request(
            "POST",
            "board/requestShutdown",
            auth=auth,
            params=params,
            json_body=None,
            files=None,
        )
        # Most endpoints return JSON
        try:
            return resp.json()
        except ValueError:
            return resp.text

    def restart_sun_autofocus(self, auth: str) -> Any:
        """POST /v1/sun/restartAutofocus
        Requires: Authorization header
        Return (Android/Kotlin signature): (Ljava/lang/String;Lkotlin/coroutines/Continuation<-Lcom/vaonis/instruments/sdk/models/response/OrderResponse;>;)Ljava/lang/Object;
        """
        params = None
        resp = self._request(
            "POST",
            "sun/restartAutofocus",
            auth=auth,
            params=params,
            json_body=None,
            files=None,
        )
        # Most endpoints return JSON
        try:
            return resp.json()
        except ValueError:
            return resp.text

    def send_sun_mode_action(self, auth: str, body: Any) -> Any:
        """POST /v1/sun/handleUserAction
        Requires: Authorization header
        JSON body: Lcom/vaonis/instruments/sdk/models/body/SunModeActionBody;
        Return (Android/Kotlin signature): (Ljava/lang/String;Lcom/vaonis/instruments/sdk/models/body/SunModeActionBody;Lkotlin/coroutines/Continuation<-Lcom/vaonis/instruments/sdk/models/response/OrderResponse;>;)Ljava/lang/Object;
        """
        params = None
        resp = self._request(
            "POST",
            "sun/handleUserAction",
            auth=auth,
            params=params,
            json_body=body,
            files=None,
        )
        # Most endpoints return JSON
        try:
            return resp.json()
        except ValueError:
            return resp.text

    def set_sun_mode_params(self, auth: str, body: Any) -> Any:
        """POST /v1/sun/setUserParams
        Requires: Authorization header
        JSON body: Lcom/vaonis/instruments/sdk/models/body/SunModeParamsBody;
        Return (Android/Kotlin signature): (Ljava/lang/String;Lcom/vaonis/instruments/sdk/models/body/SunModeParamsBody;Lkotlin/coroutines/Continuation<-Lcom/vaonis/instruments/sdk/models/response/OrderResponse;>;)Ljava/lang/Object;
        """
        params = None
        resp = self._request(
            "POST",
            "sun/setUserParams",
            auth=auth,
            params=params,
            json_body=body,
            files=None,
        )
        # Most endpoints return JSON
        try:
            return resp.json()
        except ValueError:
            return resp.text

    def set_to_be_resumable(self, auth: str) -> Any:
        """POST /v1/capture/setToBeResumable
        Requires: Authorization header
        Return (Android/Kotlin signature): (Ljava/lang/String;Lkotlin/coroutines/Continuation<-Lcom/vaonis/instruments/sdk/models/response/OrderResponse;>;)Ljava/lang/Object;
        """
        params = None
        resp = self._request(
            "POST",
            "capture/setToBeResumable",
            auth=auth,
            params=params,
            json_body=None,
            files=None,
        )
        # Most endpoints return JSON
        try:
            return resp.json()
        except ValueError:
            return resp.text

    def start_auto_init(self, auth: str, body: Any) -> Any:
        """POST /v1/general/startAutoInit
        Requires: Authorization header
        JSON body: Lcom/vaonis/instruments/sdk/models/body/AutoInitBody;
        Return (Android/Kotlin signature): (Ljava/lang/String;Lcom/vaonis/instruments/sdk/models/body/AutoInitBody;Lkotlin/coroutines/Continuation<-Lcom/vaonis/instruments/sdk/models/response/OrderResponse;>;)Ljava/lang/Object;
        """
        params = None
        resp = self._request(
            "POST",
            "general/startAutoInit",
            auth=auth,
            params=params,
            json_body=body,
            files=None,
        )
        # Most endpoints return JSON
        try:
            return resp.json()
        except ValueError:
            return resp.text

    def start_observation(self, auth: str, body: Any) -> Any:
        """POST /v1/general/startObservation
        Requires: Authorization header
        JSON body: Lcom/vaonis/instruments/sdk/models/body/StartObservationBody;
        Return (Android/Kotlin signature): (Ljava/lang/String;Lcom/vaonis/instruments/sdk/models/body/StartObservationBody;Lkotlin/coroutines/Continuation<-Lcom/vaonis/instruments/sdk/models/response/OrderResponse;>;)Ljava/lang/Object;
        """
        params = None
        resp = self._request(
            "POST",
            "general/startObservation",
            auth=auth,
            params=params,
            json_body=body,
            files=None,
        )
        # Most endpoints return JSON
        try:
            return resp.json()
        except ValueError:
            return resp.text

    def start_observation_from_stored_capture(self, auth: str, body: Any) -> Any:
        """POST /v1/captureStore/startObservationFromStoredCapture
        Requires: Authorization header
        JSON body: Lcom/vaonis/instruments/sdk/models/body/StartObservationFromStoredCaptureBody;
        Return (Android/Kotlin signature): (Ljava/lang/String;Lcom/vaonis/instruments/sdk/models/body/StartObservationFromStoredCaptureBody;Lkotlin/coroutines/Continuation<-Lcom/vaonis/instruments/sdk/models/response/OrderResponse;>;)Ljava/lang/Object;
        """
        params = None
        resp = self._request(
            "POST",
            "captureStore/startObservationFromStoredCapture",
            auth=auth,
            params=params,
            json_body=body,
            files=None,
        )
        # Most endpoints return JSON
        try:
            return resp.json()
        except ValueError:
            return resp.text

    def start_plan(self, auth: str, body: Any) -> Any:
        """POST /v1/planner/startPlan
        Requires: Authorization header
        JSON body: Lcom/vaonis/instruments/sdk/models/body/planmynight/PlanMyNightBody;
        Return (Android/Kotlin signature): (Ljava/lang/String;Lcom/vaonis/instruments/sdk/models/body/planmynight/PlanMyNightBody;Lkotlin/coroutines/Continuation<-Lcom/vaonis/instruments/sdk/models/response/OrderResponse;>;)Ljava/lang/Object;
        """
        params = None
        resp = self._request(
            "POST",
            "planner/startPlan",
            auth=auth,
            params=params,
            json_body=body,
            files=None,
        )
        # Most endpoints return JSON
        try:
            return resp.json()
        except ValueError:
            return resp.text

    def start_playlist(self, auth: str, body: Any) -> Any:
        """POST /v1/playlist/startPlaylist
        Requires: Authorization header
        JSON body: Lcom/vaonis/instruments/sdk/models/body/PlaylistBody;
        Return (Android/Kotlin signature): (Ljava/lang/String;Lcom/vaonis/instruments/sdk/models/body/PlaylistBody;Lkotlin/coroutines/Continuation<-Lcom/vaonis/instruments/sdk/models/response/OrderResponse;>;)Ljava/lang/Object;
        """
        params = None
        resp = self._request(
            "POST",
            "playlist/startPlaylist",
            auth=auth,
            params=params,
            json_body=body,
            files=None,
        )
        # Most endpoints return JSON
        try:
            return resp.json()
        except ValueError:
            return resp.text

    def start_storage_acquisition(self, auth: str, body: Any) -> Any:
        """POST /v1/expertMode/startStorageAcquisition
        Requires: Authorization header
        JSON body: Lcom/vaonis/instruments/sdk/models/body/StorageAcquisitionBody;
        Return (Android/Kotlin signature): (Ljava/lang/String;Lcom/vaonis/instruments/sdk/models/body/StorageAcquisitionBody;Lkotlin/coroutines/Continuation<-Lcom/vaonis/instruments/sdk/models/response/OrderResponse;>;)Ljava/lang/Object;
        """
        params = None
        resp = self._request(
            "POST",
            "expertMode/startStorageAcquisition",
            auth=auth,
            params=params,
            json_body=body,
            files=None,
        )
        # Most endpoints return JSON
        try:
            return resp.json()
        except ValueError:
            return resp.text

    def start_sun_mode(self, auth: str, body: Any) -> Any:
        """POST /v1/sun/startSunMode
        Requires: Authorization header
        JSON body: Lcom/vaonis/instruments/sdk/models/body/SunModeBody;
        Return (Android/Kotlin signature): (Ljava/lang/String;Lcom/vaonis/instruments/sdk/models/body/SunModeBody;Lkotlin/coroutines/Continuation<-Lcom/vaonis/instruments/sdk/models/response/OrderResponse;>;)Ljava/lang/Object;
        """
        params = None
        resp = self._request(
            "POST",
            "sun/startSunMode",
            auth=auth,
            params=params,
            json_body=body,
            files=None,
        )
        # Most endpoints return JSON
        try:
            return resp.json()
        except ValueError:
            return resp.text

    def stop_auto_init(self, auth: str) -> Any:
        """POST /v1/general/stopAutoInit
        Requires: Authorization header
        Return (Android/Kotlin signature): (Ljava/lang/String;Lkotlin/coroutines/Continuation<-Lcom/vaonis/instruments/sdk/models/response/OrderResponse;>;)Ljava/lang/Object;
        """
        params = None
        resp = self._request(
            "POST",
            "general/stopAutoInit",
            auth=auth,
            params=params,
            json_body=None,
            files=None,
        )
        # Most endpoints return JSON
        try:
            return resp.json()
        except ValueError:
            return resp.text

    def stop_generate_dark(self, auth: str) -> Any:
        """POST /v1/darkManager/stopGenerateDark
        Requires: Authorization header
        Return (Android/Kotlin signature): (Ljava/lang/String;Lkotlin/coroutines/Continuation<-Lcom/vaonis/instruments/sdk/models/response/OrderResponse;>;)Ljava/lang/Object;
        """
        params = None
        resp = self._request(
            "POST",
            "darkManager/stopGenerateDark",
            auth=auth,
            params=params,
            json_body=None,
            files=None,
        )
        # Most endpoints return JSON
        try:
            return resp.json()
        except ValueError:
            return resp.text

    def stop_observation(self, auth: str) -> Any:
        """POST /v1/general/stopObservation
        Requires: Authorization header
        Return (Android/Kotlin signature): (Ljava/lang/String;Lkotlin/coroutines/Continuation<-Lcom/vaonis/instruments/sdk/models/response/OrderResponse;>;)Ljava/lang/Object;
        """
        params = None
        resp = self._request(
            "POST",
            "general/stopObservation",
            auth=auth,
            params=params,
            json_body=None,
            files=None,
        )
        # Most endpoints return JSON
        try:
            return resp.json()
        except ValueError:
            return resp.text

    def stop_plan(self, auth: str) -> Any:
        """POST /v1/planner/stopPlan
        Requires: Authorization header
        Return (Android/Kotlin signature): (Ljava/lang/String;Lkotlin/coroutines/Continuation<-Lcom/vaonis/instruments/sdk/models/response/OrderResponse;>;)Ljava/lang/Object;
        """
        params = None
        resp = self._request(
            "POST",
            "planner/stopPlan",
            auth=auth,
            params=params,
            json_body=None,
            files=None,
        )
        # Most endpoints return JSON
        try:
            return resp.json()
        except ValueError:
            return resp.text

    def stop_playlist(self, auth: str) -> Any:
        """POST /v1/playlist/stopPlaylist
        Requires: Authorization header
        Return (Android/Kotlin signature): (Ljava/lang/String;Lkotlin/coroutines/Continuation<-Lcom/vaonis/instruments/sdk/models/response/OrderResponse;>;)Ljava/lang/Object;
        """
        params = None
        resp = self._request(
            "POST",
            "playlist/stopPlaylist",
            auth=auth,
            params=params,
            json_body=None,
            files=None,
        )
        # Most endpoints return JSON
        try:
            return resp.json()
        except ValueError:
            return resp.text

    def stop_storage_acquisition(self, auth: str) -> Any:
        """POST /v1/expertMode/stopStorageAcquisition
        Requires: Authorization header
        Return (Android/Kotlin signature): (Ljava/lang/String;Lkotlin/coroutines/Continuation<-Lcom/vaonis/instruments/sdk/models/response/OrderResponse;>;)Ljava/lang/Object;
        """
        params = None
        resp = self._request(
            "POST",
            "expertMode/stopStorageAcquisition",
            auth=auth,
            params=params,
            json_body=None,
            files=None,
        )
        # Most endpoints return JSON
        try:
            return resp.json()
        except ValueError:
            return resp.text

    def stop_sun_observation(self, auth: str) -> Any:
        """POST /v1/sun/stopObservation
        Requires: Authorization header
        Return (Android/Kotlin signature): (Ljava/lang/String;Lkotlin/coroutines/Continuation<-Lcom/vaonis/instruments/sdk/models/response/OrderResponse;>;)Ljava/lang/Object;
        """
        params = None
        resp = self._request(
            "POST",
            "sun/stopObservation",
            auth=auth,
            params=params,
            json_body=None,
            files=None,
        )
        # Most endpoints return JSON
        try:
            return resp.json()
        except ValueError:
            return resp.text

    def switch_frequency(self, auth: str, body: Any) -> Any:
        """POST /v1/network/switchFrequency
        Requires: Authorization header
        JSON body: Lcom/vaonis/instruments/sdk/models/body/NetworkBody;
        Return (Android/Kotlin signature): (Ljava/lang/String;Lcom/vaonis/instruments/sdk/models/body/NetworkBody;Lkotlin/coroutines/Continuation<-Lkotlin/Unit;>;)Ljava/lang/Object;
        """
        params = None
        resp = self._request(
            "POST",
            "network/switchFrequency",
            auth=auth,
            params=params,
            json_body=body,
            files=None,
        )
        # Most endpoints return JSON
        try:
            return resp.json()
        except ValueError:
            return resp.text

    def update_settings(self, auth: str, body: Any) -> Any:
        """POST /v1/app/setSettings
        Requires: Authorization header
        JSON body: Lcom/vaonis/instruments/sdk/models/body/SettingsBody;
        Return (Android/Kotlin signature): (Ljava/lang/String;Lcom/vaonis/instruments/sdk/models/body/SettingsBody;Lkotlin/coroutines/Continuation<-Lcom/vaonis/instruments/sdk/models/response/OrderResponse;>;)Ljava/lang/Object;
        """
        params = None
        resp = self._request(
            "POST",
            "app/setSettings",
            auth=auth,
            params=params,
            json_body=body,
            files=None,
        )
        # Most endpoints return JSON
        try:
            return resp.json()
        except ValueError:
            return resp.text

    def upload_update_file(
        self, auth: str, file_name: Any, model: Any, file: Any
    ) -> Any:
        """POST /v1/updates/uploadUpdateFile
        Requires: Authorization header
        Query params: fileName, model
        Multipart part: Lokhttp3/MultipartBody$Part;
        Return (Android/Kotlin signature): (Ljava/lang/String;Lokhttp3/MultipartBody$Part;Ljava/lang/String;Ljava/lang/String;)Lretrofit2/Call<Lokhttp3/ResponseBody;>;
        """
        params: Dict[str, Any] = {}
        params["fileName"] = file_name
        params["model"] = model
        # NOTE: The Android client uses MultipartBody.Part which embeds its own form name/filename.
        # Here we assume the server expects a part named "file"; adjust if your device expects a different form field.
        resp = self._request(
            "POST",
            "updates/uploadUpdateFile",
            auth=auth,
            params=params,
            json_body=None,
            files={"file": file},
        )
        # Most endpoints return JSON
        try:
            return resp.json()
        except ValueError:
            return resp.text

    def download_image(
        self, url: str, stream: bool = False, auth: Optional[str] = None
    ) -> Any:
        """GET an arbitrary URL with streaming enabled (mirrors StellinaAPI.downloadImage).

        This is a thin convenience wrapper around requests; pass either a full URL or a path.
        """
        if url.startswith("http://") or url.startswith("https://"):
            full_url = url
        else:
            full_url = self.base_url.rstrip("/") + "/" + url.lstrip("/")
        self._log("HTTP image request GET %s", full_url)
        headers: Dict[str, str] = {}
        if auth is not None:
            headers["Authorization"] = auth
        resp = requests.get(
            full_url, timeout=self.timeout_s, stream=stream, headers=headers
        )
        if stream:
            return resp
        content = resp.content
        content_type = resp.headers.get("content-type")
        self._log(
            "HTTP image response %s status=%s bytes=%s",
            full_url,
            resp.status_code,
            len(content),
        )
        if resp.ok or _looks_like_image(content, content_type):
            return content
        resp.raise_for_status()
        return content
