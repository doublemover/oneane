from __future__ import annotations

from typing import Any, Optional

import pytest


@pytest.fixture
def gui_app(monkeypatch: pytest.MonkeyPatch):
    try:
        import tkinter as tk
    except Exception:  # pragma: no cover
        pytest.skip("Tkinter not available")

    from vaonis_instruments import gui_app as gui

    try:
        root = tk.Tk()
        root.withdraw()
    except Exception:
        pytest.skip("Tkinter UI not available in this environment")

    monkeypatch.setattr(gui.BarnardControlApp, "_auto_load_auth_key", lambda self: None)
    monkeypatch.setattr(gui.BarnardControlApp, "_schedule_log_pump", lambda self: None)
    app = gui.BarnardControlApp(root)

    yield app

    root.destroy()


def test_timestamp_normalization(gui_app) -> None:
    app = gui_app
    assert app._normalize_timestamp_to_ms("123") == 123000
    assert app._normalize_timestamp_to_ms(123.0) == 123000
    assert app._normalize_timestamp_to_ms(1710000000000) == 1710000000000


def test_extract_device_timestamp(gui_app) -> None:
    app = gui_app
    status = {"result": {"timestamp": 100}}
    assert app._extract_device_timestamp(status) == 100000


def test_status_summary_lines(gui_app) -> None:
    app = gui_app
    status = {
        "result": {
            "telescopeId": "scope",
            "instrumentState": "READY",
            "bootCount": 3,
        }
    }
    lines = app._build_status_summary_lines(status, max_lines=3)
    assert len(lines) == 3
    assert any("telescopeId" in line for line in lines)


def test_prefill_operation_fields(gui_app) -> None:
    app = gui_app
    route = {"method": "POST", "path": "/general/adjustObservationFocus"}
    app._prefill_operation_fields(route)
    params = app.params_text.get("1.0", "end").strip()
    body = app.body_text.get("1.0", "end").strip()

    assert params == "{}"
    assert "restartCapture" in body


def test_auto_time_sync(gui_app, monkeypatch: pytest.MonkeyPatch) -> None:
    app = gui_app

    class DummySocket:
        def __init__(self) -> None:
            self.calls: list[tuple[int, bool]] = []

        def set_system_time(
            self, timestamp_ms: int, *, use_object: bool = False
        ) -> None:
            self.calls.append((timestamp_ms, use_object))

    socket = DummySocket()
    app.socket_client = socket

    monkeypatch.setattr("vaonis_instruments.gui_app.time.time", lambda: 100.0)
    monkeypatch.setattr("vaonis_instruments.gui_app.time.monotonic", lambda: 200.0)

    app._maybe_sync_time({"result": {"timestamp": 90}})

    assert socket.calls == [(100000, False)]


def test_should_auto_live_view(gui_app) -> None:
    app = gui_app
    status_idle = {"result": {"currentOperation": {"state": "IDLE"}}}
    status_running = {"result": {"currentOperation": {"state": "RUNNING"}}}

    assert app._should_auto_live_view(status_idle) is False
    assert app._should_auto_live_view(status_running) is True
    app.auto_live_var.set(False)
    assert app._should_auto_live_view(status_running) is False


def test_update_image_url_triggers_live_view(
    gui_app, monkeypatch: pytest.MonkeyPatch
) -> None:
    app = gui_app
    app.auto_live_var.set(True)
    app.live_view_running = False

    started: list[bool] = []

    def fake_start() -> None:
        started.append(True)
        app.live_view_running = True

    class DummyNotebook:
        def __init__(self) -> None:
            self.selected = None

        def select(self, tab) -> None:
            self.selected = tab

    app._notebook = DummyNotebook()
    monkeypatch.setattr(app, "_start_live_view", fake_start)

    status = {"result": {"previewUrl": "/image/preview.jpg"}}
    app._update_image_url_from_status(status)

    assert app.image_url_var.get() == "/image/preview.jpg"
    assert started
    assert app._notebook.selected is app.image_tab


def test_set_response_applies_tags(gui_app) -> None:
    app = gui_app
    app._set_response({"count": 2, "name": "scope", "flag": True})
    content = app.response_text.get("1.0", "end").strip()
    assert '"count"' in content
    assert '"name"' in content


def test_flatten_status_and_stringify(gui_app) -> None:
    app = gui_app
    status = {"result": {"list": [1, 2], "nested": {"value": "x"}}}
    flattened = app._flatten_status(status)
    assert "result.list[0]" in flattened
    assert "result.nested.value" in flattened
    assert app._stringify_value("x" * 500).endswith("(truncated)")


def test_update_status_controls_updates_tree(gui_app) -> None:
    app = gui_app
    status = {"result": {"telescopeId": "scope", "bootCount": 1}}
    app._update_status_controls(status)
    assert app.status_items
