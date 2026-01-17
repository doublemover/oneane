"""Tkinter GUI for the Barnard instrument API."""

from __future__ import annotations

import io
import json
import logging
import queue
import re
import signal
import threading
import time
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from pathlib import Path

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

try:
    from PIL import Image, ImageTk  # type: ignore

    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

from .auth import AuthContext, build_authorization_header
from .auth_key_extractor import ensure_auth_key
from .logging_utils import find_repo_root, setup_logging
from .socket_client import VaonisSocketClient
from .unified_client import DEFAULT_PREFIXES, UnifiedHTTPClient

TIME_SYNC_THRESHOLD_MS = 5000
TIME_SYNC_COOLDOWN_SEC = 60


def _safe_json_load(text: str) -> Any:
    raw = text.strip()
    if not raw:
        return None
    return json.loads(raw)


def _format_json(value: Any) -> str:
    try:
        return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True)
    except TypeError:
        return str(value)


def _looks_like_url(value: str) -> bool:
    return value.startswith("http://") or value.startswith("https://")


def _image_extension(data: bytes, content_type: Optional[str]) -> str:
    if content_type:
        ct = content_type.lower()
        if "png" in ct:
            return ".png"
        if "jpeg" in ct or "jpg" in ct:
            return ".jpg"
        if "gif" in ct:
            return ".gif"
        if "bmp" in ct:
            return ".bmp"
        if "tiff" in ct:
            return ".tiff"
        if "webp" in ct:
            return ".webp"
    if data[:3] == b"\xff\xd8\xff":
        return ".jpg"
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return ".png"
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return ".gif"
    if data[:2] == b"BM":
        return ".bmp"
    if data[:4] in (b"II*\x00", b"MM\x00*"):
        return ".tiff"
    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return ".webp"
    return ".bin"


def _find_image_urls(payload: Any) -> List[str]:
    urls: List[str] = []

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            for key, val in value.items():
                if isinstance(val, str) and (
                    "image" in key.lower()
                    or "preview" in key.lower()
                    or "thumbnail" in key.lower()
                ):
                    urls.append(val)
                else:
                    walk(val)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(payload)
    return [u for u in urls if isinstance(u, str)]


class QueueLogHandler(logging.Handler):
    def __init__(self, log_queue: "queue.Queue[str]") -> None:
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
        except Exception:
            msg = record.getMessage()
        self.log_queue.put(msg)


class ToolTip:
    def __init__(
        self,
        widget: tk.Widget,
        text: str,
        *,
        delay_ms: int = 750,
        background: str = "SystemInfoBackground",
        foreground: str = "SystemInfoText",
        wrap_length: int = 360,
    ) -> None:
        self.widget = widget
        self.text = text
        self.delay_ms = delay_ms
        self.background = background
        self.foreground = foreground
        self.wrap_length = wrap_length
        self._after_id: Optional[str] = None
        self._tip_window: Optional[tk.Toplevel] = None
        self._fade_after_id: Optional[str] = None

        widget.bind("<Enter>", self._on_enter)
        widget.bind("<Leave>", self._on_leave)
        widget.bind("<ButtonPress>", self._on_leave)

    def _on_enter(self, *_: Any) -> None:
        self._schedule()

    def _on_leave(self, *_: Any) -> None:
        self._cancel()
        self._fade_out()

    def _schedule(self) -> None:
        self._cancel()
        self._after_id = self.widget.after(self.delay_ms, self._show)

    def _cancel(self) -> None:
        if self._after_id is not None:
            try:
                self.widget.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

    def _show(self) -> None:
        if self._tip_window is not None or not self.text:
            return
        tip = tk.Toplevel(self.widget)
        tip.wm_overrideredirect(True)
        try:
            tip.wm_attributes("-topmost", True)
        except Exception:
            pass
        try:
            tip.wm_attributes("-alpha", 0.0)
        except Exception:
            pass
        label = tk.Label(
            tip,
            text=self.text,
            justify="left",
            background=self.background,
            foreground=self.foreground,
            relief="solid",
            borderwidth=1,
            wraplength=self.wrap_length,
            padx=8,
            pady=4,
        )
        label.pack()
        tip.update_idletasks()
        tip_w = tip.winfo_width()
        tip_h = tip.winfo_height()
        screen_w = tip.winfo_screenwidth()
        screen_h = tip.winfo_screenheight()
        widget_x = self.widget.winfo_rootx()
        widget_y = self.widget.winfo_rooty()
        widget_h = self.widget.winfo_height()
        x = widget_x + 16
        y = widget_y + widget_h + 12
        if y + tip_h > screen_h - 8:
            y = widget_y - tip_h - 12
        if y < 0:
            y = 8
        if x + tip_w > screen_w - 8:
            x = max(8, screen_w - tip_w - 8)
        tip.wm_geometry(f"+{x}+{y}")
        self._tip_window = tip
        self._fade_in()

    def _hide(self) -> None:
        if self._fade_after_id is not None:
            try:
                self.widget.after_cancel(self._fade_after_id)
            except Exception:
                pass
            self._fade_after_id = None
        if self._tip_window is not None:
            self._tip_window.destroy()
            self._tip_window = None

    def _fade_in(self, step: int = 0) -> None:
        if self._tip_window is None:
            return
        try:
            alpha = min(1.0, step / 6)
            self._tip_window.wm_attributes("-alpha", alpha)
        except Exception:
            return
        if alpha < 1.0:
            self._fade_after_id = self.widget.after(15, lambda: self._fade_in(step + 1))

    def _fade_out(self, step: int = 0) -> None:
        if self._tip_window is None:
            return
        try:
            alpha = max(0.0, 1.0 - (step / 6))
            self._tip_window.wm_attributes("-alpha", alpha)
        except Exception:
            self._hide()
            return
        if alpha > 0.0:
            self._fade_after_id = self.widget.after(
                15, lambda: self._fade_out(step + 1)
            )
        else:
            self._hide()


class BarnardControlApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Barnard Instrument Control")
        self.root.geometry("900x770")

        self._theme = self._apply_theme()

        self.log_queue: "queue.Queue[str]" = queue.Queue()
        self.http_log = setup_logging("http")
        self.socket_log = setup_logging("socket")
        self.gui_log = setup_logging("gui")

        self.log_handler = QueueLogHandler(self.log_queue)
        self.log_handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
        )
        self.http_log.logger.addHandler(self.log_handler)
        self.socket_log.logger.addHandler(self.log_handler)
        self.gui_log.logger.addHandler(self.log_handler)

        self.auth_header: Optional[str] = None
        self.auth_key_path: Optional[str] = None
        self.last_status: Optional[Dict[str, Any]] = None
        self.last_image_bytes: Optional[bytes] = None
        self.last_image_content_type: Optional[str] = None
        self.live_view_running = False
        self.socket_client: Optional[VaonisSocketClient] = None
        self._notebook: Optional[ttk.Notebook] = None
        self.status_items: Dict[str, str] = {}
        self.status_values: Dict[str, str] = {}
        self._schema_cache: Dict[Path, Dict[str, Any]] = {}
        self._schema_bundle_by_name: Dict[str, Dict[str, Any]] = {}
        self._schema_bundle_routes: Dict[Tuple[str, str], Dict[str, Any]] = {}
        self._request_schema_by_route: Dict[
            Tuple[str, str], Union[Path, Dict[str, Any]]
        ] = {}
        self._query_params_by_route: Dict[Tuple[str, str], List[str]] = {}
        self._operation_groups: Dict[str, List[str]] = {}
        self._debug_operation_groups: Dict[str, List[str]] = {}
        self._operation_items: List[str] = []
        self._debug_operation_items: List[str] = []
        self._operation_group_labels: Dict[str, str] = {}
        self._debug_group_labels: Dict[str, str] = {}
        self._group_label_width = 32
        self.time_sync_notice_var = tk.StringVar(value="")
        self.time_sync_notice_label: Optional[ttk.Label] = None
        self._last_time_sync_at: Optional[float] = None
        self._closing = False

        self._build_ui()
        self._register_exit_handlers()
        self._schedule_log_pump()
        self._auto_load_auth_key()

    def _register_exit_handlers(self) -> None:
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        def handle_signal(*_: object) -> None:
            self.root.after(0, self._on_close)

        try:
            signal.signal(signal.SIGINT, handle_signal)
        except Exception:
            pass

        for sequence in ("<Control-c>", "<Command-c>", "<Command-q>"):
            try:
                self.root.bind_all(sequence, lambda _event: self._on_close(), add="+")
            except Exception:
                continue

    def _on_close(self) -> None:
        if self._closing:
            return
        self._closing = True
        self.live_view_running = False
        if self.socket_client:
            try:
                self.socket_client.disconnect()
            except Exception as exc:
                self.gui_log.logger.warning("Socket disconnect failed: %s", exc)
        try:
            self.root.quit()
        finally:
            self.root.destroy()

    def _add_tooltip(self, widget: tk.Widget, text: str) -> None:
        if self._theme is None:
            ToolTip(widget, text)
            return
        ToolTip(
            widget,
            text,
            background=self._theme["panel"],
            foreground=self._theme["text"],
        )

    def _apply_theme(self) -> Optional[Dict[str, str]]:
        """Apply a sane default ttk theme and a small amount of spacing polish.

        This keeps the UI looking consistent across platforms without forcing a
        custom color palette (tk.Text widgets are not ttk-themed).
        """
        style = ttk.Style(self.root)

        # Pick the best available theme for the platform.
        for candidate in ("vista", "xpnative", "clam", "default"):
            if candidate in style.theme_names():
                try:
                    style.theme_use(candidate)
                    break
                except tk.TclError:
                    continue

        # Global spacing/typography tweaks.
        try:
            style.configure("TNotebook.Tab", padding=(12, 6))
        except tk.TclError:
            pass
        style.configure("TLabelframe", padding=(10, 8))
        style.configure("TLabelframe.Label", font=("TkDefaultFont", 9, "bold"))

        style.configure("Header.TFrame", padding=(10, 8, 10, 6))
        style.configure("HeaderTitle.TLabel", font=("TkDefaultFont", 10, "bold"))
        style.configure("Muted.TLabel", foreground="#555555")

        # Quick-start buttons should align with the left edge of their label text.
        style.configure("Quick.TButton", anchor="w")

        return None

    def _style_text(self, widget: tk.Text) -> None:
        if self._theme is None:
            return
        options = {
            "background": self._theme["entry_bg"],
            "foreground": self._theme["text"],
            "insertbackground": self._theme["text"],
            "selectbackground": self._theme["select_bg"],
            "selectforeground": self._theme["text"],
            "disabledbackground": self._theme["entry_bg"],
            "disabledforeground": self._theme["text_dim"],
        }
        available = set(widget.keys())
        safe_options = {
            key: value for key, value in options.items() if key in available
        }
        widget.configure(**safe_options)

    def _build_ui(self) -> None:
        main_pane = ttk.PanedWindow(self.root, orient=tk.VERTICAL)
        main_pane.pack(fill=tk.BOTH, expand=True)

        top_frame = ttk.Frame(main_pane)
        console_frame = ttk.Frame(main_pane)
        main_pane.add(top_frame, weight=3)
        main_pane.add(console_frame, weight=1)

        # Header
        header_frame = ttk.Frame(top_frame, style="Header.TFrame")
        header_frame.pack(fill=tk.X)
        header_frame.columnconfigure(0, weight=2)
        header_frame.columnconfigure(1, weight=1)

        quick_frame = ttk.LabelFrame(header_frame, text="Quick start", padding=(8, 6))
        quick_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        quick_frame.columnconfigure(0, weight=1)

        quick_font = ("TkDefaultFont", 9)

        style = ttk.Style()
        style.configure("Quick.TButton", anchor="w")

        step0_label = ttk.Label(
            quick_frame,
            text="Set Host/Port + API base path (instrument IP).",
            font=quick_font,
            style="Muted.TLabel",
        )
        step0_label.grid(row=0, column=0, sticky="w", columnspan=2)

        step1_label = ttk.Label(
            quick_frame, text="1) Load/extract auth key from APK/ZIP.", font=quick_font
        )
        step1_label.grid(row=1, column=0, sticky="w", pady=(6, 0))
        load_key_button = ttk.Button(
            quick_frame,
            text="Load/Extract key",
            command=self._auto_load_auth_key,
            width=24,
            style="Quick.TButton",
        )
        load_key_button.grid(row=1, column=1, sticky="e", padx=(8, 0), pady=(6, 0))
        self.load_key_button = load_key_button

        step2_label = ttk.Label(
            quick_frame,
            text="2) Refresh auth + status (reads challenge).",
            font=quick_font,
        )
        step2_label.grid(row=2, column=0, sticky="w", pady=(4, 0))
        refresh_button = ttk.Button(
            quick_frame,
            text="Refresh auth + status",
            command=self._refresh_auth_and_status,
            width=24,
            style="Quick.TButton",
        )
        refresh_button.grid(row=2, column=1, sticky="e", padx=(8, 0), pady=(4, 0))

        step3_label = ttk.Label(
            quick_frame,
            text="3) Connect socket for live updates.",
            font=quick_font,
        )
        step3_label.grid(row=3, column=0, sticky="w", pady=(4, 0))
        socket_button = ttk.Button(
            quick_frame,
            text="Connect socket",
            command=self._connect_socket,
            width=24,
            style="Quick.TButton",
        )
        socket_button.grid(row=3, column=1, sticky="e", padx=(8, 0), pady=(4, 0))

        # Status summary: use a Label rather than a Text widget.
        summary_frame = ttk.LabelFrame(header_frame, text="Status", padding=(8, 6))
        summary_frame.grid(row=0, column=1, sticky="nsew")
        summary_frame.columnconfigure(0, weight=1)

        self.status_summary_var = tk.StringVar(value="(no status yet)")
        self.status_summary_label = ttk.Label(
            summary_frame,
            textvariable=self.status_summary_var,
            justify="left",
            anchor="w",
            wraplength=420,
        )
        self.status_summary_label.grid(row=0, column=0, sticky="ew")

        # Tooltips
        self._add_tooltip(
            step0_label, "Set the instrument IP/port and base path before anything."
        )
        self._add_tooltip(
            step1_label, "Extract the auth key from the APK/ZIP (saved locally)."
        )
        self._add_tooltip(load_key_button, "Load or extract the auth key now.")
        self._add_tooltip(
            step2_label, "Fetch /app/status to build the Authorization header."
        )
        self._add_tooltip(
            refresh_button, "Fetch status and compute Authorization header."
        )
        self._add_tooltip(step3_label, "Connect Socket.IO to stream status updates.")
        self._add_tooltip(socket_button, "Connect Socket.IO for live updates.")
        self._add_tooltip(
            self.status_summary_label, "Live highlights from the most recent status."
        )

        # Tabs
        self._notebook = ttk.Notebook(top_frame)
        self._notebook.pack(fill=tk.BOTH, expand=True, padx=6, pady=(2, 6))

        self.connection_tab = ttk.Frame(self._notebook)
        self.status_tab = ttk.Frame(self._notebook)
        self.http_tab = ttk.Frame(self._notebook)
        self.socket_tab = ttk.Frame(self._notebook)
        self.image_tab = ttk.Frame(self._notebook)

        self._notebook.add(self.connection_tab, text="Connection")
        self._notebook.add(self.status_tab, text="Status")
        self._notebook.add(self.http_tab, text="HTTP")
        self._notebook.add(self.socket_tab, text="Socket")
        self._notebook.add(self.image_tab, text="Images")

        self._build_connection_tab()
        self._build_status_tab()
        self._build_http_tab()
        self._build_socket_tab()
        self._build_image_tab()
        self._build_console_tab(console_frame)

    def _build_connection_tab(self) -> None:
        outer = ttk.Frame(self.connection_tab, padding=10)
        outer.pack(fill=tk.BOTH, expand=True)
        outer.columnconfigure(0, weight=1)
        outer.columnconfigure(1, weight=1)
        outer.rowconfigure(0, weight=0)
        outer.rowconfigure(1, weight=0)

        # State variables used by the rest of the app.
        self.host_var = tk.StringVar(value="10.0.0.1")
        self.port_var = tk.StringVar(value="8082")
        self.api_path_var = tk.StringVar(value="/v1")
        self.prefixes_var = tk.StringVar(value=", ".join(DEFAULT_PREFIXES))
        self.use_auth_var = tk.BooleanVar(value=True)
        self.auth_key_var = tk.StringVar(value="")
        self.auth_header_var = tk.StringVar(value="")

        show_advanced_var = tk.BooleanVar(value=False)

        def toggle_advanced() -> None:
            if show_advanced_var.get():
                advanced_row.grid()
            else:
                advanced_row.grid_remove()

        # Instrument section
        instrument = ttk.Labelframe(outer, text="Instrument", padding=(10, 8))
        instrument.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))
        instrument.columnconfigure(1, weight=1)

        host_label = ttk.Label(instrument, text="Host:")
        host_label.grid(row=0, column=0, sticky="e", padx=(0, 8), pady=2)
        host_entry = ttk.Entry(instrument, textvariable=self.host_var)
        host_entry.grid(row=0, column=1, sticky="ew", pady=2)

        port_label = ttk.Label(instrument, text="Port:")
        port_label.grid(row=1, column=0, sticky="e", padx=(0, 8), pady=2)
        port_entry = ttk.Entry(instrument, textvariable=self.port_var, width=8)
        port_entry.grid(row=1, column=1, sticky="w", pady=2)

        api_label = ttk.Label(instrument, text="API base path:")
        api_label.grid(row=2, column=0, sticky="e", padx=(0, 8), pady=2)
        api_entry = ttk.Entry(instrument, textvariable=self.api_path_var, width=12)
        api_entry.grid(row=2, column=1, sticky="w", pady=2)

        advanced_toggle = ttk.Checkbutton(
            instrument,
            text="Show advanced settings",
            variable=show_advanced_var,
            command=toggle_advanced,
        )
        advanced_toggle.grid(row=3, column=0, columnspan=2, sticky="w", pady=(6, 0))

        advanced_row = ttk.Frame(instrument)
        advanced_row.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        advanced_row.columnconfigure(1, weight=1)

        prefixes_label = ttk.Label(advanced_row, text="Prefixes:")
        prefixes_label.grid(row=0, column=0, sticky="e", padx=(0, 8), pady=2)
        prefixes_entry = ttk.Entry(advanced_row, textvariable=self.prefixes_var)
        prefixes_entry.grid(row=0, column=1, sticky="ew", pady=2)
        advanced_row.grid_remove()

        # Authorization section
        auth = ttk.Labelframe(outer, text="Authorization", padding=(10, 8))
        auth.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=(0, 10))
        auth.columnconfigure(1, weight=1)

        auth_check = ttk.Checkbutton(
            auth,
            text="Include Authorization header by default",
            variable=self.use_auth_var,
        )
        auth_check.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 6))

        key_label = ttk.Label(auth, text="Auth key path:")
        key_label.grid(row=1, column=0, sticky="e", padx=(0, 8), pady=2)
        key_entry = ttk.Entry(auth, textvariable=self.auth_key_var, state="readonly")
        key_entry.grid(row=1, column=1, sticky="ew", pady=2)
        key_button = ttk.Button(
            auth, text="Load/Extract", command=self._auto_load_auth_key
        )
        key_button.grid(row=1, column=2, sticky="e", padx=(8, 0), pady=2)

        header_label = ttk.Label(auth, text="Auth header:")
        header_label.grid(row=2, column=0, sticky="e", padx=(0, 8), pady=2)
        header_entry = ttk.Entry(
            auth, textvariable=self.auth_header_var, state="readonly"
        )
        header_entry.grid(row=2, column=1, sticky="ew", pady=2)
        header_button = ttk.Button(auth, text="Refresh", command=self._refresh_auth)
        header_button.grid(row=2, column=2, sticky="e", padx=(8, 0), pady=2)

        # Actions section
        actions = ttk.Labelframe(outer, text="Actions", padding=(10, 8))
        actions.grid(row=1, column=0, columnspan=2, sticky="ew")
        actions.columnconfigure(0, weight=1)

        bar = ttk.Frame(actions)
        bar.grid(row=0, column=0, sticky="ew")
        bar.columnconfigure(0, weight=1)

        left = ttk.Frame(bar)
        left.grid(row=0, column=0, sticky="w")
        detect_button = ttk.Button(
            left, text="Detect base URL", command=self._detect_base_url
        )
        detect_button.grid(row=0, column=0, padx=(0, 10))

        right = ttk.Frame(bar)
        right.grid(row=0, column=1, sticky="e")
        fetch_button = ttk.Button(right, text="Fetch status", command=self._fetch_status)
        fetch_button.grid(row=0, column=0)

        # Tooltips
        self._add_tooltip(
            host_label, "Instrument IP or hostname (default: 10.0.0.1 on device AP)."
        )
        self._add_tooltip(host_entry, "Instrument IP or hostname.")
        self._add_tooltip(
            port_label, "HTTP port for the instrument API (default: 8082)."
        )
        self._add_tooltip(port_entry, "HTTP port for the instrument API.")
        self._add_tooltip(api_label, "Base API path (default: /v1). Usually unchanged.")
        self._add_tooltip(api_entry, "Base API path (default: /v1).")
        self._add_tooltip(
            prefixes_label,
            "Prefixes are URL path probes used to find the device (e.g., /stellina/http).",
        )
        self._add_tooltip(
            prefixes_entry, "Comma-separated prefixes to probe when detecting base URL."
        )
        self._add_tooltip(
            advanced_toggle,
            "Show/hide advanced connection settings (prefix probing).",
        )
        self._add_tooltip(
            auth_check, "Include Authorization header automatically on HTTP requests."
        )
        self._add_tooltip(key_label, "Location of the local .auth_key file.")
        self._add_tooltip(
            key_entry,
            "Local auth key (base64). This is stored in src/python/.auth_key.",
        )
        self._add_tooltip(
            key_button,
            "Extract key from APK/ZIP if missing, or reload from disk.",
        )
        self._add_tooltip(
            header_label, "Authorization header built from /app/status challenge."
        )
        self._add_tooltip(header_entry, "Current Authorization header (read-only).")
        self._add_tooltip(
            header_button, "Fetch /app/status and rebuild Authorization header."
        )
        self._add_tooltip(fetch_button, "Fetch /app/status (also refreshes auth).")
        self._add_tooltip(detect_button, "Probe prefixes to find a working base URL.")

    def _build_http_tab(self) -> None:
        outer = ttk.Frame(self.http_tab, padding=10)
        outer.pack(fill=tk.BOTH, expand=True)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(3, weight=1)

        # Operation selectors
        ops = ttk.Labelframe(outer, text="Operation", padding=(10, 8))
        ops.grid(row=0, column=0, sticky="ew")
        ops.columnconfigure(1, weight=0)
        ops.columnconfigure(3, weight=1)

        operation_group_label = ttk.Label(ops, text="Operation group")
        operation_group_label.grid(row=0, column=0, sticky="w")
        self.operation_group_var = tk.StringVar()
        self.operation_group_combo = ttk.Combobox(
            ops,
            textvariable=self.operation_group_var,
            width=self._group_label_width,
            font=("TkFixedFont", 9),
        )
        self.operation_group_combo.grid(row=0, column=1, sticky="w")
        self.operation_group_combo.bind(
            "<<ComboboxSelected>>", self._on_operation_group_selected
        )

        operation_label = ttk.Label(ops, text="Operation")
        operation_label.grid(row=0, column=2, sticky="w", padx=(12, 0))
        self.operation_var = tk.StringVar()
        self.operation_combo = ttk.Combobox(ops, textvariable=self.operation_var)
        self.operation_combo.grid(row=0, column=3, sticky="ew")
        self.operation_combo.bind("<<ComboboxSelected>>", self._on_operation_selected)

        debug_group_label = ttk.Label(ops, text="Debug group")
        debug_group_label.grid(row=1, column=0, sticky="w", pady=(6, 0))
        self.debug_group_var = tk.StringVar()
        self.debug_group_combo = ttk.Combobox(
            ops,
            textvariable=self.debug_group_var,
            width=self._group_label_width,
            font=("TkFixedFont", 9),
        )
        self.debug_group_combo.grid(row=1, column=1, sticky="w", pady=(6, 0))
        self.debug_group_combo.bind(
            "<<ComboboxSelected>>", self._on_debug_group_selected
        )

        debug_label = ttk.Label(ops, text="Debug operation")
        debug_label.grid(row=1, column=2, sticky="w", padx=(12, 0), pady=(6, 0))
        self.debug_operation_var = tk.StringVar()
        self.debug_operation_combo = ttk.Combobox(
            ops, textvariable=self.debug_operation_var
        )
        self.debug_operation_combo.grid(row=1, column=3, sticky="ew", pady=(6, 0))
        self.debug_operation_combo.bind(
            "<<ComboboxSelected>>", self._on_debug_operation_selected
        )

        self.operation_detail_var = tk.StringVar(value="")
        operation_detail = ttk.Label(ops, textvariable=self.operation_detail_var, style="Muted.TLabel")
        operation_detail.grid(row=2, column=1, columnspan=3, sticky="w", pady=(6, 0))

        # Request editors
        request = ttk.Labelframe(outer, text="Request", padding=(10, 8))
        request.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        request.columnconfigure(0, weight=1)

        request_nb = ttk.Notebook(request)
        request_nb.grid(row=0, column=0, sticky="ew")

        # Query params tab
        params_tab = ttk.Frame(request_nb, padding=(6, 6))
        params_tab.columnconfigure(0, weight=1)
        params_tab.rowconfigure(0, weight=1)

        self.params_text = tk.Text(
            params_tab,
            height=6,
            width=70,
            wrap="none",
            font=("TkFixedFont", 9),
        )
        self._style_text(self.params_text)
        params_scroll = ttk.Scrollbar(
            params_tab, orient="vertical", command=self.params_text.yview
        )
        params_hscroll = ttk.Scrollbar(
            params_tab, orient="horizontal", command=self.params_text.xview
        )
        self.params_text.configure(
            yscrollcommand=params_scroll.set, xscrollcommand=params_hscroll.set
        )
        self.params_text.grid(row=0, column=0, sticky="nsew")
        params_scroll.grid(row=0, column=1, sticky="ns")
        params_hscroll.grid(row=1, column=0, sticky="ew")

        # Body tab
        body_tab = ttk.Frame(request_nb, padding=(6, 6))
        body_tab.columnconfigure(0, weight=1)
        body_tab.rowconfigure(0, weight=1)

        self.body_text = tk.Text(
            body_tab,
            height=10,
            width=70,
            wrap="none",
            font=("TkFixedFont", 9),
        )
        self._style_text(self.body_text)
        body_scroll = ttk.Scrollbar(
            body_tab, orient="vertical", command=self.body_text.yview
        )
        body_hscroll = ttk.Scrollbar(
            body_tab, orient="horizontal", command=self.body_text.xview
        )
        self.body_text.configure(
            yscrollcommand=body_scroll.set, xscrollcommand=body_hscroll.set
        )
        self.body_text.grid(row=0, column=0, sticky="nsew")
        body_scroll.grid(row=0, column=1, sticky="ns")
        body_hscroll.grid(row=1, column=0, sticky="ew")

        request_nb.add(params_tab, text="Query params (JSON)")
        request_nb.add(body_tab, text="Body (JSON)")

        # Actions row
        actions = ttk.Frame(outer)
        actions.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        actions.columnconfigure(0, weight=1)

        send_button = ttk.Button(actions, text="Send", command=self._send_operation)
        clear_button = ttk.Button(actions, text="Clear", command=self._clear_operation_fields)
        clear_button.grid(row=0, column=2, sticky="e")
        send_button.grid(row=0, column=1, sticky="e", padx=(0, 10))

        # Response
        response = ttk.Labelframe(outer, text="Response", padding=(10, 8))
        response.grid(row=3, column=0, sticky="nsew", pady=(10, 0))
        response.columnconfigure(0, weight=1)
        response.rowconfigure(0, weight=1)

        self.response_text = tk.Text(
            response,
            height=10,
            width=90,
            state="disabled",
            wrap="none",
            font=("TkFixedFont", 9),
        )
        self._style_text(self.response_text)
        response_scroll = ttk.Scrollbar(
            response, orient="vertical", command=self.response_text.yview
        )
        response_hscroll = ttk.Scrollbar(
            response, orient="horizontal", command=self.response_text.xview
        )
        self.response_text.configure(
            yscrollcommand=response_scroll.set, xscrollcommand=response_hscroll.set
        )
        self.response_text.grid(row=0, column=0, sticky="nsew")
        response_scroll.grid(row=0, column=1, sticky="ns")
        response_hscroll.grid(row=1, column=0, sticky="ew")

        # Response syntax highlight colors tuned for a light background.
        self.response_text.tag_configure("json_key", foreground="#1f4e79")
        self.response_text.tag_configure("json_string", foreground="#006100")
        self.response_text.tag_configure("json_number", foreground="#7f6000")
        self.response_text.tag_configure("json_bool", foreground="#7f0000")

        # Tooltips
        self._add_tooltip(
            operation_group_label, "Filter operations by the first route segment."
        )
        self._add_tooltip(
            self.operation_group_combo,
            "Choose a route group to narrow the operation list.",
        )
        self._add_tooltip(operation_label, "Pick an API operation from the catalog.")
        self._add_tooltip(
            self.operation_combo,
            "Operations map to APK-defined routes and methods.",
        )
        self._add_tooltip(debug_group_label, "Group filter for debug-only routes.")
        self._add_tooltip(
            self.debug_group_combo, "Choose a debug route group to narrow the list."
        )
        self._add_tooltip(
            debug_label, "Debug-only routes (separated from normal operations)."
        )
        self._add_tooltip(
            self.debug_operation_combo, "Select only if you need debug behavior."
        )
        self._add_tooltip(
            operation_detail, "Shows HTTP method and route for the selection."
        )
        self._add_tooltip(
            self.params_text,
            "Query params JSON. Use {} if no parameters are required.",
        )
        self._add_tooltip(self.body_text, "Request body JSON for POST/PUT endpoints.")
        self._add_tooltip(send_button, "Send the selected API request.")
        self._add_tooltip(clear_button, "Clear params/body editor fields.")
        self._add_tooltip(self.response_text, "Response data (read-only).")

        self._load_operations()

    def _build_status_tab(self) -> None:
        frame = ttk.Frame(self.status_tab, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        status_label = ttk.Label(frame, text="Live status values")
        status_label.pack(anchor="w")
        self.status_tree = ttk.Treeview(
            frame, columns=("key", "value"), show="headings", height=20
        )
        self.status_tree.heading("key", text="Key")
        self.status_tree.heading("value", text="Value")
        self.status_tree.column("key", width=300, anchor="w")
        self.status_tree.column("value", width=700, anchor="w")
        self.status_tree.tag_configure("changed", background="#fff2cc")
        self.status_tree.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(
            frame, orient="vertical", command=self.status_tree.yview
        )
        self.status_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._add_tooltip(
            status_label, "Flattened status fields updated from HTTP + socket."
        )
        self._add_tooltip(
            self.status_tree, "Live status values; changes highlight as they update."
        )

    def _build_socket_tab(self) -> None:
        outer = ttk.Frame(self.socket_tab, padding=10)
        outer.pack(fill=tk.BOTH, expand=True)
        outer.columnconfigure(0, weight=1)
        outer.columnconfigure(1, weight=1)
        outer.rowconfigure(2, weight=1)

        self.socket_url_var = tk.StringVar(value="http://10.0.0.1:8083")
        self.socket_path_var = tk.StringVar(value="/socket.io")
        self.socket_device_var = tk.StringVar(value="")
        self.socket_name_var = tk.StringVar(value="")
        self.socket_country_var = tk.StringVar(value="")

        # Connection
        conn = ttk.Labelframe(outer, text="Socket connection", padding=(10, 8))
        conn.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))
        conn.columnconfigure(1, weight=1)

        socket_url_label = ttk.Label(conn, text="Socket URL:")
        socket_url_label.grid(row=0, column=0, sticky="e", padx=(0, 8), pady=2)
        socket_url_entry = ttk.Entry(conn, textvariable=self.socket_url_var)
        socket_url_entry.grid(row=0, column=1, sticky="ew", pady=2)

        socket_path_label = ttk.Label(conn, text="Path:")
        socket_path_label.grid(row=1, column=0, sticky="e", padx=(0, 8), pady=2)
        socket_path_entry = ttk.Entry(conn, textvariable=self.socket_path_var, width=14)
        socket_path_entry.grid(row=1, column=1, sticky="w", pady=2)

        device_label = ttk.Label(conn, text="Device ID:")
        device_label.grid(row=2, column=0, sticky="e", padx=(0, 8), pady=2)
        device_entry = ttk.Entry(conn, textvariable=self.socket_device_var)
        device_entry.grid(row=2, column=1, sticky="ew", pady=2)

        btn_row = ttk.Frame(conn)
        btn_row.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        connect_button = ttk.Button(btn_row, text="Connect", command=self._connect_socket)
        disconnect_button = ttk.Button(btn_row, text="Disconnect", command=self._disconnect_socket)
        connect_button.grid(row=0, column=0, padx=(0, 10))
        disconnect_button.grid(row=0, column=1)

        # Registration
        reg = ttk.Labelframe(outer, text="Registration", padding=(10, 8))
        reg.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=(0, 10))
        reg.columnconfigure(1, weight=1)

        name_label = ttk.Label(reg, text="Name:")
        name_label.grid(row=0, column=0, sticky="e", padx=(0, 8), pady=2)
        name_entry = ttk.Entry(reg, textvariable=self.socket_name_var)
        name_entry.grid(row=0, column=1, sticky="ew", pady=2)

        country_label = ttk.Label(reg, text="Country:")
        country_label.grid(row=1, column=0, sticky="e", padx=(0, 8), pady=2)
        country_entry = ttk.Entry(reg, textvariable=self.socket_country_var, width=10)
        country_entry.grid(row=1, column=1, sticky="w", pady=2)

        user_label = ttk.Label(reg, text="User name:")
        user_label.grid(row=2, column=0, sticky="e", padx=(0, 8), pady=(10, 2))
        self.socket_user_var = tk.StringVar(value="")
        user_entry = ttk.Entry(reg, textvariable=self.socket_user_var)
        user_entry.grid(row=2, column=1, sticky="ew", pady=(10, 2))
        send_user_button = ttk.Button(reg, text="Send user", command=self._set_user_name)
        send_user_button.grid(row=3, column=1, sticky="e", pady=(6, 0))

        # Commands
        commands = ttk.Labelframe(outer, text="Commands", padding=(10, 8))
        commands.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        take_button = ttk.Button(commands, text="Take control", command=self._take_control)
        release_button = ttk.Button(commands, text="Release control", command=self._release_control)
        restart_button = ttk.Button(commands, text="Restart app", command=self._restart_app)
        shutdown_button = ttk.Button(commands, text="Shutdown", command=self._shutdown)

        take_button.grid(row=0, column=0, padx=(0, 10), pady=2)
        release_button.grid(row=0, column=1, padx=(0, 10), pady=2)
        restart_button.grid(row=0, column=2, padx=(0, 10), pady=2)
        shutdown_button.grid(row=0, column=3, pady=2)

        self.time_sync_notice_label = ttk.Label(commands, textvariable=self.time_sync_notice_var, style="Muted.TLabel")
        self.time_sync_notice_label.grid(row=1, column=0, columnspan=4, sticky="w", pady=(8, 0))
        self.time_sync_notice_label.grid_remove()

        # Raw events
        raw = ttk.Labelframe(outer, text="Raw event", padding=(10, 8))
        raw.grid(row=2, column=0, columnspan=2, sticky="nsew")
        raw.columnconfigure(1, weight=1)
        raw.rowconfigure(1, weight=1)

        raw_label = ttk.Label(raw, text="Event name:")
        raw_label.grid(row=0, column=0, sticky="e", padx=(0, 8), pady=2)
        self.socket_command_var = tk.StringVar(value="")
        raw_entry = ttk.Entry(raw, textvariable=self.socket_command_var)
        raw_entry.grid(row=0, column=1, sticky="ew", pady=2)
        send_raw_button = ttk.Button(raw, text="Send", command=self._send_raw_socket)
        send_raw_button.grid(row=0, column=2, sticky="e", padx=(8, 0), pady=2)

        payload_label = ttk.Label(raw, text="Payload (JSON):")
        payload_label.grid(row=1, column=0, sticky="ne", padx=(0, 8), pady=(8, 0))

        payload_frame = ttk.Frame(raw)
        payload_frame.grid(row=1, column=1, columnspan=2, sticky="nsew", pady=(8, 0))
        payload_frame.columnconfigure(0, weight=1)
        payload_frame.rowconfigure(0, weight=1)

        self.socket_payload_text = tk.Text(payload_frame, height=6, width=60, wrap="none", font=("TkFixedFont", 9))
        self._style_text(self.socket_payload_text)
        payload_scroll = ttk.Scrollbar(payload_frame, orient="vertical", command=self.socket_payload_text.yview)
        payload_hscroll = ttk.Scrollbar(payload_frame, orient="horizontal", command=self.socket_payload_text.xview)
        self.socket_payload_text.configure(yscrollcommand=payload_scroll.set, xscrollcommand=payload_hscroll.set)
        self.socket_payload_text.grid(row=0, column=0, sticky="nsew")
        payload_scroll.grid(row=0, column=1, sticky="ns")
        payload_hscroll.grid(row=1, column=0, sticky="ew")

        # Tooltips
        self._add_tooltip(
            socket_url_label, "Socket.IO server URL (default: http://10.0.0.1:8083)."
        )
        self._add_tooltip(socket_url_entry, "Socket.IO server URL.")
        self._add_tooltip(socket_path_label, "Socket.IO path (default: /socket.io).")
        self._add_tooltip(socket_path_entry, "Socket.IO path.")
        self._add_tooltip(
            device_label, "Device ID (auto-filled from status when available)."
        )
        self._add_tooltip(device_entry, "Device ID to register with the socket.")
        self._add_tooltip(name_label, "Client name used in socket registration.")
        self._add_tooltip(name_entry, "Client name to send with socket requests.")
        self._add_tooltip(country_label, "Country code for socket registration.")
        self._add_tooltip(country_entry, "ISO country code (e.g., US).")
        self._add_tooltip(connect_button, "Open the Socket.IO connection.")
        self._add_tooltip(disconnect_button, "Close the Socket.IO connection.")
        self._add_tooltip(take_button, "Request control of the instrument.")
        self._add_tooltip(release_button, "Release control of the instrument.")
        self._add_tooltip(restart_button, "Restart the device app.")
        self._add_tooltip(shutdown_button, "Shutdown the device.")
        self._add_tooltip(
            self.time_sync_notice_label,
            "Appears only when a significant time drift is detected.",
        )
        self._add_tooltip(user_label, "User name to associate with this session.")
        self._add_tooltip(user_entry, "User name to send with socket commands.")
        self._add_tooltip(send_user_button, "Send the user name command.")
        self._add_tooltip(raw_label, "Send a raw socket event by name.")
        self._add_tooltip(raw_entry, "Socket event name.")
        self._add_tooltip(self.socket_payload_text, "Raw socket payload JSON.")
        self._add_tooltip(send_raw_button, "Send raw socket event with payload.")

    def _build_image_tab(self) -> None:
        outer = ttk.Frame(self.image_tab, padding=10)
        outer.pack(fill=tk.BOTH, expand=True)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(1, weight=1)

        self.image_url_var = tk.StringVar(value="")
        self.live_interval_var = tk.StringVar(value="2.0")
        self.auto_live_var = tk.BooleanVar(value=True)

        controls = ttk.Labelframe(outer, text="Controls", padding=(10, 8))
        controls.grid(row=0, column=0, sticky="ew")
        controls.columnconfigure(1, weight=1)

        image_label = ttk.Label(controls, text="Image URL or path:")
        image_label.grid(row=0, column=0, sticky="e", padx=(0, 8), pady=2)
        image_entry = ttk.Entry(controls, textvariable=self.image_url_var)
        image_entry.grid(row=0, column=1, columnspan=4, sticky="ew", pady=2)

        fetch_button = ttk.Button(controls, text="Fetch", command=self._fetch_image)
        save_button = ttk.Button(controls, text="Save", command=self._save_image)
        live_button = ttk.Button(controls, text="Start live view", command=self._start_live_view)
        stop_button = ttk.Button(controls, text="Stop", command=self._stop_live_view)

        fetch_button.grid(row=1, column=1, sticky="w", pady=(8, 0))
        save_button.grid(row=1, column=2, sticky="w", pady=(8, 0), padx=(10, 0))
        live_button.grid(row=1, column=3, sticky="w", pady=(8, 0), padx=(10, 0))
        stop_button.grid(row=1, column=4, sticky="w", pady=(8, 0), padx=(10, 0))

        interval_label = ttk.Label(controls, text="Live interval (s):")
        interval_label.grid(row=2, column=0, sticky="e", padx=(0, 8), pady=(10, 2))
        interval_entry = ttk.Entry(controls, textvariable=self.live_interval_var, width=8)
        interval_entry.grid(row=2, column=1, sticky="w", pady=(10, 2))
        auto_check = ttk.Checkbutton(
            controls,
            text="Auto-start live view when image updates",
            variable=self.auto_live_var,
        )
        auto_check.grid(row=2, column=2, columnspan=3, sticky="w", pady=(10, 2))

        preview = ttk.Labelframe(outer, text="Preview", padding=(10, 8))
        preview.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        preview.columnconfigure(0, weight=1)
        preview.rowconfigure(0, weight=1)

        self.image_label = ttk.Label(preview, text="No image loaded", anchor="center")
        self.image_label.grid(row=0, column=0, sticky="nsew")

        self._add_tooltip(
            image_label, "Image URL/path (auto-populated from status when available)."
        )
        self._add_tooltip(image_entry, "Paste or auto-filled image path to fetch.")
        self._add_tooltip(fetch_button, "Download and preview the image.")
        self._add_tooltip(save_button, "Save the last downloaded image to disk.")
        self._add_tooltip(live_button, "Start polling the image URL on a timer.")
        self._add_tooltip(stop_button, "Stop live view polling.")
        self._add_tooltip(interval_label, "Seconds between live view fetches.")
        self._add_tooltip(interval_entry, "Live view interval in seconds.")
        self._add_tooltip(
            auto_check, "Automatically start live view when status includes images."
        )
        self._add_tooltip(self.image_label, "Image preview area.")

    def _build_console_tab(self, parent: tk.Widget) -> None:
        frame = ttk.Frame(parent, padding=(10, 6, 10, 10))
        frame.pack(fill=tk.BOTH, expand=True)

        toolbar = ttk.Frame(frame)
        toolbar.pack(fill=tk.X)
        ttk.Label(toolbar, text="Logs", style="HeaderTitle.TLabel").pack(side=tk.LEFT)

        clear_btn = ttk.Button(toolbar, text="Clear", command=lambda: self._clear_console())
        clear_btn.pack(side=tk.RIGHT)

        console_frame = ttk.Frame(frame)
        console_frame.pack(fill=tk.BOTH, expand=True, pady=(6, 0))
        console_frame.columnconfigure(0, weight=1)
        console_frame.rowconfigure(0, weight=1)

        self.console_text = tk.Text(
            console_frame,
            height=10,
            width=120,
            state="disabled",
            wrap="word",
            font=("TkFixedFont", 9),
        )
        self._style_text(self.console_text)
        self.console_text.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(console_frame, command=self.console_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.console_text.configure(yscrollcommand=scrollbar.set)

        # Log tag colors tuned for a light background.
        self.console_text.tag_configure("log_info", foreground="#006100")
        self.console_text.tag_configure("log_warning", foreground="#7f6000")
        self.console_text.tag_configure("log_error", foreground="#7f0000")

        self._add_tooltip(self.console_text, "Logs for HTTP, socket, and GUI actions.")
        self._add_tooltip(clear_btn, "Clear the log output.")

    def _clear_console(self) -> None:
        if not hasattr(self, "console_text"):
            return
        self.console_text.configure(state="normal")
        self.console_text.delete("1.0", tk.END)
        self.console_text.configure(state="disabled")

    def _schedule_log_pump(self) -> None:
        while True:
            try:
                message = self.log_queue.get_nowait()
            except queue.Empty:
                break
            self._append_console(message)
        self.root.after(200, self._schedule_log_pump)

    def _append_console(self, message: str) -> None:
        self.console_text.configure(state="normal")
        line_start = self.console_text.index(tk.END)
        self.console_text.insert(tk.END, message + "\n")
        line_end = self.console_text.index(tk.END)
        tag = None
        if " ERROR " in message or " EXCEPTION " in message:
            tag = "log_error"
        elif " WARNING " in message:
            tag = "log_warning"
        elif " INFO " in message:
            tag = "log_info"
        if tag:
            self.console_text.tag_add(tag, line_start, line_end)
        self.console_text.see(tk.END)
        self.console_text.configure(state="disabled")

    def _run_in_thread(
        self, action: Callable[[], Any], on_success: Callable[[Any], None]
    ) -> None:
        def runner() -> None:
            try:
                result = action()
            except Exception as exc:
                self.gui_log.logger.exception("Action failed: %s", exc)
                self.root.after(0, lambda: messagebox.showerror("Error", str(exc)))
                return
            self.root.after(0, lambda: on_success(result))

        threading.Thread(target=runner, daemon=True).start()

    def _auto_load_auth_key(self) -> None:
        key_path = Path(__file__).resolve().parents[1] / ".auth_key"
        if key_path.exists() and key_path.read_text(encoding="utf-8").strip():
            self.auth_key_path = str(key_path)
            self.auth_key_var.set(str(key_path))
            self.gui_log.logger.info("Auth key already present at %s", key_path)
            self._set_load_key_state(loaded=True)
            return

        root = find_repo_root()
        candidates: List[Path] = []
        preferred = root / "com.vaonis.barnard.zip"
        if preferred.exists():
            candidates.append(preferred)
        for ext in (".apk", ".xapk", ".zip"):
            for path in root.glob(f"*{ext}"):
                if path not in candidates:
                    candidates.append(path)

        input_path: Optional[Path] = candidates[0] if candidates else None
        if input_path is None:
            selected = filedialog.askopenfilename(
                title="Select Barnard APK/XAPK/ZIP",
                filetypes=[("APK or ZIP", "*.apk *.zip *.xapk"), ("All files", "*.*")],
            )
            if not selected:
                self.gui_log.logger.info("Auth key load canceled by user.")
                return
            input_path = Path(selected)

        self.auth_key_var.set("Extracting auth key...")
        self.gui_log.logger.info("Extracting auth key from %s", input_path)

        def load() -> str:
            path = ensure_auth_key(input_path=input_path)
            return str(path)

        def done(path: str) -> None:
            self.auth_key_path = path
            self.auth_key_var.set(path)
            self.gui_log.logger.info("Auth key loaded from %s", path)
            self._set_load_key_state(loaded=True)

        self._run_in_thread(load, done)

    def _set_load_key_state(self, *, loaded: bool) -> None:
        if not hasattr(self, "load_key_button"):
            return
        if loaded:
            self.load_key_button.configure(
                text="Key loaded", state="disabled", style="Quick.TButton"
            )
        else:
            self.load_key_button.configure(
                text="Load/Extract key", state="normal", style="Quick.TButton"
            )

    def _build_auth_from_status(self, status: Any) -> Optional[str]:
        if not isinstance(status, dict):
            return None
        result = status.get("result")
        if not isinstance(result, dict):
            return None
        try:
            ctx = AuthContext(
                challenge=result["challenge"],
                telescope_id=result["telescopeId"],
                boot_count=result["bootCount"],
            )
        except KeyError:
            return None
        return build_authorization_header(ctx)

    def _refresh_auth(self) -> None:
        def action() -> str:
            client = self._build_http_client()
            status = client.request("GET", "app/status")
            self._update_status_cache(status)
            auth_header = self._build_auth_from_status(status)
            if not auth_header:
                raise ValueError("Status response missing auth fields.")
            return auth_header

        def done(auth_header: str) -> None:
            self.auth_header = auth_header
            self.auth_header_var.set(auth_header)

        self._run_in_thread(action, done)

    def _fetch_status(self) -> None:
        if self.use_auth_var.get():
            self._refresh_auth_and_status()
            return

        def action() -> Any:
            client = self._build_http_client()
            return client.request("GET", "app/status")

        def done(result: Any) -> None:
            self._update_status_cache(result)
            self._set_response(result)
            self._update_image_url_from_status(result)

        self._run_in_thread(action, done)

    def _refresh_auth_and_status(self) -> None:
        def action() -> Tuple[str, Any]:
            client = self._build_http_client()
            status = client.request("GET", "app/status")
            self._update_status_cache(status)
            auth_header = self._build_auth_from_status(status)
            if not auth_header:
                raise ValueError("Status response missing auth fields.")
            return auth_header, status

        def done(result: Tuple[str, Any]) -> None:
            auth_header, status = result
            self.auth_header = auth_header
            self.auth_header_var.set(auth_header)
            self._set_response(status)
            self._update_image_url_from_status(status)

        self._run_in_thread(action, done)

    def _detect_base_url(self) -> None:
        def action() -> str:
            client = self._build_http_client()
            return client.detect_base_url()

        def done(base_url: str) -> None:
            self._set_response({"baseUrl": base_url})

        self._run_in_thread(action, done)

    def _load_operations(self) -> None:
        routes_path = (
            Path(__file__).resolve().parent / "data" / "http_routes_union.json"
        )
        routes_list = json.loads(routes_path.read_text(encoding="utf-8"))
        routes = {item["operationId"]: item for item in routes_list}
        self._request_schema_by_route = self._load_request_schema_by_route()
        self._query_params_by_route = self._load_query_params_by_route()
        items: List[str] = []
        debug_items: List[str] = []
        self._operation_lookup: Dict[str, Dict[str, Any]] = {}
        self._operation_groups = {}
        self._debug_operation_groups = {}
        for operation_id, route in sorted(routes.items()):
            label = f"{operation_id} ({route['method']} {route['path']})"
            path_value = str(route.get("path", ""))
            group = self._route_group(path_value)
            if self._is_debug_operation(operation_id, path_value):
                debug_items.append(label)
                self._debug_operation_groups.setdefault(group, []).append(label)
            else:
                items.append(label)
                self._operation_groups.setdefault(group, []).append(label)
            self._operation_lookup[label] = route
        self._operation_items = items
        self._debug_operation_items = debug_items

        op_labels, op_map = self._build_group_labels(
            self._operation_groups, len(items), self._group_label_width
        )
        self._operation_group_labels = op_map
        self.operation_group_combo["values"] = op_labels
        if op_labels:
            self.operation_group_var.set(op_labels[0])
        else:
            self.operation_group_var.set("")
        self._update_operation_combo(from_debug=False)

        if not debug_items:
            self.debug_group_combo.configure(state="disabled")
            self.debug_operation_combo.configure(state="disabled")
            self.debug_group_var.set("")
            self.debug_operation_var.set("")
            self._debug_group_labels = {}
        else:
            self.debug_group_combo.configure(state="normal")
            self.debug_operation_combo.configure(state="normal")
            debug_labels, debug_map = self._build_group_labels(
                self._debug_operation_groups,
                len(debug_items),
                self._group_label_width,
            )
            self._debug_group_labels = debug_map
            self.debug_group_combo["values"] = debug_labels
            if debug_labels:
                self.debug_group_var.set(debug_labels[0])
            else:
                self.debug_group_var.set("")
            self._update_operation_combo(from_debug=True)

    def _on_operation_selected(self, event: Optional[Any] = None) -> None:
        self._select_operation(self.operation_var.get(), from_debug=False)

    def _on_debug_operation_selected(self, event: Optional[Any] = None) -> None:
        self._select_operation(self.debug_operation_var.get(), from_debug=True)

    def _on_operation_group_selected(self, event: Optional[Any] = None) -> None:
        self._update_operation_combo(from_debug=False)

    def _on_debug_group_selected(self, event: Optional[Any] = None) -> None:
        self._update_operation_combo(from_debug=True)

    def _select_operation(self, label: str, *, from_debug: bool) -> None:
        route = self._operation_lookup.get(label)
        if not route:
            self.operation_detail_var.set("")
            return
        self.operation_var.set(label)
        if from_debug:
            self.operation_combo.set("")
        else:
            self.debug_operation_var.set("")
        self.operation_detail_var.set(f"{route['method']} {route['path']}")
        self._prefill_operation_fields(route)

    def _clear_operation_fields(self) -> None:
        self.params_text.delete("1.0", tk.END)
        self.body_text.delete("1.0", tk.END)

    def _route_group(self, path: str) -> str:
        trimmed = path.strip("/")
        if not trimmed:
            return "root"
        return trimmed.split("/", 1)[0]

    def _build_group_labels(
        self, groups: Dict[str, List[str]], total: int, width: int
    ) -> Tuple[List[str], Dict[str, str]]:
        if not groups:
            return [], {}
        labels: List[str] = []
        mapping: Dict[str, str] = {}

        def format_label(name: str, count: int) -> str:
            count_text = f"({count})"
            left_width = max(width - len(count_text), len(name) + 1)
            padded = name.ljust(left_width)
            return f"{padded}{count_text}"

        for name in sorted(groups.keys()):
            label = format_label(name, len(groups[name]))
            labels.append(label)
            mapping[label] = name
        all_label = format_label("All", total)
        mapping[all_label] = "All"
        return [all_label] + labels, mapping

    def _update_operation_combo(self, *, from_debug: bool) -> None:
        if from_debug:
            group = self.debug_group_var.get()
            groups = self._debug_operation_groups
            items = self._debug_operation_items
            combo = self.debug_operation_combo
            var = self.debug_operation_var
            label_map = self._debug_group_labels
        else:
            group = self.operation_group_var.get()
            groups = self._operation_groups
            items = self._operation_items
            combo = self.operation_combo
            var = self.operation_var
            label_map = self._operation_group_labels

        group_key = label_map.get(group, group)
        if group_key == "All" or not group_key:
            values = items
        else:
            values = groups.get(group_key, [])

        combo["values"] = values
        if values:
            combo.current(0)
            if from_debug:
                self._on_debug_operation_selected()
            else:
                self._on_operation_selected()
        else:
            var.set("")
            self.operation_detail_var.set("")
            self._clear_operation_fields()

    def _normalize_route_key(self, method: str, path: str) -> Tuple[str, str]:
        normalized = "/" + path.lstrip("/")
        return method.upper(), normalized

    def _load_request_schema_by_route(
        self,
    ) -> Dict[Tuple[str, str], Union[Path, Dict[str, Any]]]:
        base_path = Path(__file__).resolve().parents[2]
        bundle_path = base_path / "unified" / "schemas" / "schema_bundle.json"
        self._schema_bundle_by_name = {}
        self._schema_bundle_routes = {}
        if bundle_path.exists():
            bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
            http_bundle = bundle.get("http") or {}
            schemas_by_name = http_bundle.get("schemasByName") or http_bundle.get(
                "byName"
            )
            if isinstance(schemas_by_name, dict):
                self._schema_bundle_by_name = {
                    name: schema
                    for name, schema in schemas_by_name.items()
                    if isinstance(schema, dict)
                }
            routes = http_bundle.get("routes") or http_bundle.get("byRoute") or {}
            for route_key, route_entry in routes.items():
                if not isinstance(route_key, str):
                    continue
                if isinstance(route_entry, str):
                    route_entry = {"request": route_entry}
                if not isinstance(route_entry, dict):
                    continue
                method, _, path = route_key.partition(" ")
                if not method or not path:
                    continue
                key = self._normalize_route_key(method, path)
                self._schema_bundle_routes[key] = route_entry
            route_map: Dict[Tuple[str, str], Union[Path, Dict[str, Any]]] = {}
            for key, route_entry in self._schema_bundle_routes.items():
                request_name = route_entry.get("request")
                if isinstance(request_name, dict):
                    route_map[key] = request_name
                elif isinstance(request_name, str):
                    schema = self._schema_bundle_by_name.get(request_name)
                    if isinstance(schema, dict):
                        route_map[key] = schema
            return route_map

        endpoints_path = (
            base_path / "unified" / "data" / "api_full" / "http_endpoints.json"
        )
        schemas_root = base_path / "unified" / "schemas" / "http"
        if not endpoints_path.exists() or not schemas_root.exists():
            return {}
        endpoints = json.loads(endpoints_path.read_text(encoding="utf-8"))
        route_map = {}
        for endpoint in endpoints:
            method = str(endpoint.get("method", "")).upper()
            path = str(endpoint.get("path", ""))
            ref = endpoint.get("requestBodyRef")
            if not method or not path or not ref:
                continue
            body_name = str(ref).split("/")[-1]
            schema_path = schemas_root / f"{body_name}.json"
            if schema_path.exists():
                route_map[self._normalize_route_key(method, path)] = schema_path
        return route_map

    def _load_query_params_by_route(self) -> Dict[Tuple[str, str], List[str]]:
        if self._schema_bundle_routes:
            bundle_params: Dict[Tuple[str, str], List[str]] = {}
            for route_key, route_entry in self._schema_bundle_routes.items():
                params = route_entry.get("queryParams")
                if not isinstance(params, list):
                    continue
                cleaned = [
                    name for name in params if isinstance(name, str) and name.strip()
                ]
                if cleaned:
                    bundle_params[route_key] = cleaned
            return bundle_params

        base_path = Path(__file__).resolve().parents[2]
        endpoints_path = (
            base_path
            / "unified"
            / "data"
            / "api_extracted"
            / "stellina_api_endpoints.json"
        )
        if not endpoints_path.exists():
            return {}
        endpoints = json.loads(endpoints_path.read_text(encoding="utf-8"))
        route_map: Dict[Tuple[str, str], List[str]] = {}
        for endpoint in endpoints:
            method = str(endpoint.get("http_method", "")).upper()
            path = str(endpoint.get("path", ""))
            if not method or not path:
                continue
            params: List[str] = []
            for param in endpoint.get("params", []) or []:
                for annotation in param.get("annotations", []) or []:
                    if str(annotation.get("kind", "")).lower() != "query":
                        continue
                    elements = annotation.get("elements") or {}
                    name = elements.get("value")
                    if isinstance(name, str) and name:
                        params.append(name)
            if not params:
                continue
            key = self._normalize_route_key(method, path)
            if key in route_map:
                existing = set(route_map[key])
                for name in params:
                    if name not in existing:
                        route_map[key].append(name)
            else:
                route_map[key] = params
        return route_map

    def _load_schema(self, schema_path: Path) -> Dict[str, Any]:
        cached = self._schema_cache.get(schema_path)
        if cached is not None:
            return cached
        data = json.loads(schema_path.read_text(encoding="utf-8"))
        self._schema_cache[schema_path] = data
        return data

    def _resolve_schema_ref(
        self, ref: str, base_path: Optional[Path]
    ) -> Optional[Path]:
        if ref.startswith("#"):
            return None
        if base_path is None:
            return None
        ref_path = (base_path / ref).resolve()
        if ref_path.exists():
            return ref_path
        return None

    def _schema_ref_to_name(self, ref: str) -> Optional[str]:
        if not isinstance(ref, str):
            return None
        normalized = ref.replace("\\", "/")
        name = normalized.rsplit("/", 1)[-1]
        if name.endswith(".json"):
            name = name[:-5]
        return name or None

    def _schema_example(
        self,
        schema: Dict[str, Any],
        schema_path: Optional[Path],
        depth: int = 0,
    ) -> Any:
        if depth > 4:
            return None
        if "$ref" in schema:
            ref_value = schema["$ref"]
            ref_path = self._resolve_schema_ref(
                ref_value, schema_path.parent if schema_path else None
            )
            if ref_path is not None:
                ref_schema = self._load_schema(ref_path)
                return self._schema_example(ref_schema, ref_path, depth + 1)
            ref_name = self._schema_ref_to_name(ref_value)
            if ref_name:
                ref_schema = self._schema_bundle_by_name.get(ref_name)
                if isinstance(ref_schema, dict):
                    return self._schema_example(ref_schema, None, depth + 1)
        if "example" in schema:
            return schema["example"]
        if "default" in schema:
            return schema["default"]
        if "enum" in schema and isinstance(schema["enum"], list):
            return schema["enum"][0] if schema["enum"] else None
        for key in ("oneOf", "anyOf", "allOf"):
            if key in schema and isinstance(schema[key], list) and schema[key]:
                return self._schema_example(schema[key][0], schema_path, depth + 1)
        schema_type = schema.get("type")
        if schema_type == "object" or "properties" in schema:
            props = schema.get("properties", {}) or {}
            return {
                name: self._schema_example(value, schema_path, depth + 1)
                for name, value in props.items()
            }
        if schema_type == "array":
            items = schema.get("items")
            if items:
                return [self._schema_example(items, schema_path, depth + 1)]
            return []
        if schema_type in ("integer", "number"):
            return None
        if schema_type == "boolean":
            return False
        if schema_type == "string":
            return ""
        return None

    def _prefill_operation_fields(self, route: Dict[str, Any]) -> None:
        method = str(route.get("method", "")).upper()
        path = str(route.get("path", ""))
        self.params_text.delete("1.0", tk.END)
        self.body_text.delete("1.0", tk.END)

        route_key = self._normalize_route_key(method, path)
        query_params = self._query_params_by_route.get(route_key)
        if query_params:
            params_payload = {name: "" for name in query_params}
            self.params_text.insert(
                tk.END,
                json.dumps(params_payload, indent=2, sort_keys=True, ensure_ascii=True),
            )
        else:
            self.params_text.insert(tk.END, "{}")

        schema_entry = self._request_schema_by_route.get(route_key)
        schema = None
        schema_path = None
        if isinstance(schema_entry, Path):
            schema_path = schema_entry
            schema = self._load_schema(schema_path)
        elif isinstance(schema_entry, dict):
            schema = schema_entry
        if schema is not None:
            example = self._schema_example(schema, schema_path)
            if example is None:
                example = {}
            body_text = json.dumps(example, indent=2, sort_keys=True, ensure_ascii=True)
            self.body_text.insert(tk.END, body_text)
            return

        if method != "GET":
            self.body_text.insert(tk.END, "{}")

    def _send_operation(self) -> None:
        route_label = self.operation_var.get()
        route = self._operation_lookup.get(route_label)
        if not route:
            messagebox.showerror("Error", "Select an operation first.")
            return

        method = route["method"]
        path = route["path"]

        if method.upper() != "GET" and self._is_dangerous_path(path):
            if not messagebox.askyesno(
                "Confirm",
                f"This operation may affect device safety:\n{method} {path}\nProceed?",
            ):
                return

        try:
            params = _safe_json_load(self.params_text.get("1.0", tk.END))
        except json.JSONDecodeError as exc:
            messagebox.showerror("Invalid JSON", f"Params JSON error: {exc}")
            return

        try:
            body = _safe_json_load(self.body_text.get("1.0", tk.END))
        except json.JSONDecodeError as exc:
            messagebox.showerror("Invalid JSON", f"Body JSON error: {exc}")
            return

        def action() -> Dict[str, Any]:
            client = self._build_http_client()
            use_auth = self.use_auth_var.get()
            auth_header: Optional[str] = None
            status: Any = None
            normalized_path = path.lstrip("/")
            if use_auth and normalized_path != "app/status":
                status = client.request("GET", "app/status")
                auth_header = self._build_auth_from_status(status)
                if not auth_header:
                    raise ValueError("Status response missing auth fields.")
            response = client.request(
                method,
                path,
                auth=auth_header if use_auth else None,
                params=params if isinstance(params, dict) else None,
                json_body=body,
            )
            if use_auth and normalized_path == "app/status":
                status = response
                auth_header = self._build_auth_from_status(status)
                if not auth_header:
                    raise ValueError("Status response missing auth fields.")
            return {"response": response, "status": status, "auth": auth_header}

        def done(result: Dict[str, Any]) -> None:
            status = result.get("status")
            auth_header = result.get("auth")
            if status is not None:
                self._update_status_cache(status)
                self._update_image_url_from_status(status)
            if auth_header:
                self.auth_header = auth_header
                self.auth_header_var.set(auth_header)
            self._set_response(result.get("response"))

        self._run_in_thread(action, done)

    def _connect_socket(self) -> None:
        def action() -> VaonisSocketClient:
            client = self._build_socket_client()
            client.connect()
            return client

        def done(client: VaonisSocketClient) -> None:
            self.socket_client = client

        self._run_in_thread(action, done)

    def _disconnect_socket(self) -> None:
        if self.socket_client:
            try:
                self.socket_client.disconnect()
            except Exception as exc:
                self.gui_log.logger.exception("Socket disconnect failed: %s", exc)

    def _take_control(self) -> None:
        if self.socket_client:
            self.socket_client.take_control()

    def _release_control(self) -> None:
        if self.socket_client:
            self.socket_client.release_control()

    def _restart_app(self) -> None:
        if not messagebox.askyesno("Confirm", "Restart the device app?"):
            return
        if self.socket_client:
            self.socket_client.restart_app()

    def _shutdown(self) -> None:
        if not messagebox.askyesno("Confirm", "Shutdown the device?"):
            return
        if self.socket_client:
            self.socket_client.shutdown()

    def _set_system_time(self) -> None:
        raw = ""
        if hasattr(self, "socket_time_var"):
            raw = self.socket_time_var.get().strip()
        if raw:
            try:
                epoch_ms = int(raw)
            except ValueError:
                messagebox.showerror(
                    "Invalid time", "Epoch milliseconds must be an integer."
                )
                return
        else:
            epoch_ms = int(time.time() * 1000)
        if epoch_ms < 0 or epoch_ms > 32503680000000:
            messagebox.showerror("Invalid time", "Epoch ms out of safe bounds.")
            return
        if self.socket_client:
            self.socket_client.set_system_time(
                epoch_ms,
                use_object=(
                    self.socket_time_object_var.get()
                    if hasattr(self, "socket_time_object_var")
                    else False
                ),
            )

    def _set_user_name(self) -> None:
        if self.socket_client:
            self.socket_client.set_user_name(self.socket_user_var.get())

    def _send_raw_socket(self) -> None:
        command = self.socket_command_var.get().strip()
        if not command:
            messagebox.showerror("Missing command", "Enter a socket command.")
            return
        try:
            payload = _safe_json_load(self.socket_payload_text.get("1.0", tk.END))
        except json.JSONDecodeError as exc:
            messagebox.showerror("Invalid JSON", f"Payload JSON error: {exc}")
            return
        if self.socket_client:
            self.socket_client.send_command(command, payload)

    def _fetch_image(self) -> None:
        url = self.image_url_var.get().strip()
        if not url:
            messagebox.showerror("Missing URL", "Enter an image URL or path.")
            return

        def action() -> Tuple[bytes, Optional[str]]:
            client = self._build_http_client()
            auth_header = None
            if self.auth_header and self.use_auth_var.get():
                auth_header = self.auth_header
            content = client.download_image(url, auth=auth_header)
            content_type = None
            return content, content_type

        def done(result: Tuple[bytes, Optional[str]]) -> None:
            data, content_type = result
            self.last_image_bytes = data
            self.last_image_content_type = content_type
            self._display_image(data)

        self._run_in_thread(action, done)

    def _start_live_view(self) -> None:
        if self.live_view_running:
            return
        self.live_view_running = True
        self._schedule_live_view()

    def _stop_live_view(self) -> None:
        self.live_view_running = False

    def _schedule_live_view(self) -> None:
        if not self.live_view_running:
            return
        self._fetch_image()
        try:
            interval = float(self.live_interval_var.get().strip())
        except ValueError:
            interval = 2.0
        self.root.after(int(interval * 1000), self._schedule_live_view)

    def _save_image(self) -> None:
        if not self.last_image_bytes:
            messagebox.showerror("No image", "Fetch an image first.")
            return
        default_ext = _image_extension(
            self.last_image_bytes, self.last_image_content_type
        )
        file_path = filedialog.asksaveasfilename(
            title="Save image",
            defaultextension=default_ext,
            filetypes=[("Images", f"*{default_ext}"), ("All files", "*.*")],
        )
        if not file_path:
            return
        path = file_path
        if not path.endswith(default_ext):
            path = path + default_ext
        with open(path, "wb") as handle:
            handle.write(self.last_image_bytes)
        self.gui_log.logger.info("Saved image to %s", path)

    def _display_image(self, data: bytes) -> None:
        try:
            if PIL_AVAILABLE:
                image = Image.open(io.BytesIO(data))
                image.thumbnail((900, 600))
                self._image_tk = ImageTk.PhotoImage(image)
                self.image_label.configure(image=self._image_tk, text="")
            else:
                self._image_tk = tk.PhotoImage(data=data)
                self.image_label.configure(image=self._image_tk, text="")
        except Exception as exc:
            self.gui_log.logger.exception("Failed to display image: %s", exc)
            self.image_label.configure(text="Image loaded (preview failed)")

    def _set_response(self, result: Any) -> None:
        self.response_text.configure(state="normal")
        self.response_text.delete("1.0", tk.END)
        rendered = _format_json(result)
        self.response_text.insert(tk.END, rendered)
        self._apply_json_tags(self.response_text, rendered)
        self.response_text.configure(state="disabled")

    def _apply_json_tags(self, widget: tk.Text, content: str) -> None:
        for tag in ("json_key", "json_string", "json_number", "json_bool"):
            widget.tag_remove(tag, "1.0", tk.END)
        for line_no, line in enumerate(content.splitlines(), start=1):
            match = re.match(r'(\s*)("[^"]+")(\s*:\s*)(.*)', line)
            if not match:
                continue
            _, key, _, rest = match.groups()
            key_start = line.find(key)
            if key_start >= 0:
                key_end = key_start + len(key)
                widget.tag_add(
                    "json_key", f"{line_no}.{key_start}", f"{line_no}.{key_end}"
                )
            value_start = line.find(rest, key_start + len(key))
            if value_start < 0:
                continue
            stripped = rest.lstrip()
            offset = value_start + (len(rest) - len(stripped))
            if stripped.startswith('"'):
                end = stripped.find('"', 1)
                if end != -1:
                    widget.tag_add(
                        "json_string",
                        f"{line_no}.{offset}",
                        f"{line_no}.{offset + end + 1}",
                    )
            else:
                number_match = re.match(r"-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?", stripped)
                if number_match:
                    widget.tag_add(
                        "json_number",
                        f"{line_no}.{offset}",
                        f"{line_no}.{offset + len(number_match.group(0))}",
                    )
                else:
                    bool_match = re.match(r"(true|false|null)\b", stripped)
                    if bool_match:
                        widget.tag_add(
                            "json_bool",
                            f"{line_no}.{offset}",
                            f"{line_no}.{offset + len(bool_match.group(0))}",
                        )

    def _build_http_client(self) -> UnifiedHTTPClient:
        host = self.host_var.get().strip()
        port = int(self.port_var.get().strip())
        api_path = self.api_path_var.get().strip() or "/v1"
        prefixes_raw = self.prefixes_var.get().strip()
        prefixes = [p.strip() for p in prefixes_raw.split(",") if p.strip()]
        if not prefixes:
            prefixes = list(DEFAULT_PREFIXES)
        return UnifiedHTTPClient(
            host=host,
            port=port,
            api_base_path=api_path,
            prefixes=prefixes,
            logger=self.http_log.logger,
        )

    def _build_socket_client(self) -> VaonisSocketClient:
        client = VaonisSocketClient(
            url=self.socket_url_var.get().strip(),
            path=self.socket_path_var.get().strip(),
            device_id=self.socket_device_var.get().strip(),
            name=self.socket_name_var.get().strip(),
            country_code=self.socket_country_var.get().strip(),
            event_logger=self.socket_log.logger,
        )
        client.on_connect(self._handle_socket_connect)
        client.on_reconnect(self._handle_socket_connect)
        client.on_status_updated(self._handle_socket_status)
        return client

    def _handle_socket_connect(self, *_: Any) -> None:
        self.gui_log.logger.info("Socket connected; refreshing auth + status.")
        self.root.after(0, self._refresh_auth_and_status)

    def _handle_socket_status(self, payload: Any) -> None:
        if isinstance(payload, dict):
            self._update_status_cache(payload)
            self._update_image_url_from_status(payload)

    def _update_status_cache(self, status: Any) -> None:
        if isinstance(status, dict):
            self.last_status = status
            self._update_status_controls(status)
            self._update_status_summary(status)
            self._maybe_sync_time(status)

    def _update_image_url_from_status(self, status: Any) -> None:
        urls = _find_image_urls(status)
        if not urls:
            return
        url = urls[0]
        self.image_url_var.set(url)
        if self._should_auto_live_view(status) and not self.live_view_running:
            self._start_live_view()
            if self._notebook is not None:
                self._notebook.select(self.image_tab)

    def _should_auto_live_view(self, status: Any) -> bool:
        if not self.auto_live_var.get():
            return False
        if not isinstance(status, dict):
            return True
        result = status.get("result")
        if isinstance(result, dict):
            current = result.get("currentOperation")
            if isinstance(current, dict):
                state = current.get("state")
                if isinstance(state, str):
                    lowered = state.lower()
                    idle_tokens = (
                        "idle",
                        "none",
                        "stopped",
                        "finished",
                        "complete",
                        "done",
                    )
                    if any(token in lowered for token in idle_tokens):
                        return False
        return True

    def _flatten_status(self, payload: Any) -> Dict[str, str]:
        flattened: Dict[str, str] = {}

        def walk(value: Any, prefix: str = "") -> None:
            if isinstance(value, dict):
                for key, val in value.items():
                    path = f"{prefix}.{key}" if prefix else key
                    if isinstance(val, dict):
                        if not val:
                            flattened[path] = "{}"
                        walk(val, path)
                    elif isinstance(val, list):
                        if len(val) > 20:
                            flattened[path] = f"<list length {len(val)}>"
                        else:
                            walk(val, path)
                    else:
                        flattened[path] = self._stringify_value(val)
            elif isinstance(value, list):
                for idx, item in enumerate(value):
                    path = f"{prefix}[{idx}]"
                    if isinstance(item, (dict, list)):
                        walk(item, path)
                    else:
                        flattened[path] = self._stringify_value(item)

        walk(payload)
        return flattened

    def _extract_device_timestamp(self, status: Any) -> Optional[int]:
        if not isinstance(status, dict):
            return None
        candidates: List[Any] = []
        if "timestamp" in status:
            candidates.append(status.get("timestamp"))
        result = status.get("result")
        if isinstance(result, dict) and "timestamp" in result:
            candidates.append(result.get("timestamp"))
        for value in candidates:
            normalized = self._normalize_timestamp_to_ms(value)
            if normalized is not None:
                return normalized
        return None

    def _normalize_timestamp_to_ms(self, value: Any) -> Optional[int]:
        if isinstance(value, bool):
            return None
        if isinstance(value, (int, float)):
            numeric = float(value)
        elif isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return None
            try:
                numeric = float(stripped)
            except ValueError:
                return None
        else:
            return None
        if numeric <= 0:
            return None
        if numeric < 1e11:
            return int(numeric * 1000)
        return int(numeric)

    def _set_time_sync_notice(self, drift_ms: Optional[int], *, note: str = "") -> None:
        if self.time_sync_notice_label is None:
            return
        if drift_ms is None:
            self.time_sync_notice_var.set("")
            self.time_sync_notice_label.grid_remove()
            return
        message = f"Time drift detected: {drift_ms} ms"
        if note:
            message = f"{message} ({note})"
        self.time_sync_notice_var.set(message)
        self.time_sync_notice_label.grid()

    def _maybe_sync_time(self, status: Any) -> None:
        if self.socket_client is None:
            return
        device_ms = self._extract_device_timestamp(status)
        if device_ms is None:
            self._set_time_sync_notice(None)
            return
        now_ms = int(time.time() * 1000)
        drift_ms = abs(device_ms - now_ms)
        if drift_ms <= TIME_SYNC_THRESHOLD_MS:
            self._set_time_sync_notice(None)
            return
        now = time.monotonic()
        if self._last_time_sync_at is not None:
            if now - self._last_time_sync_at < TIME_SYNC_COOLDOWN_SEC:
                self._set_time_sync_notice(drift_ms, note="auto-sync pending")
                return
        self._last_time_sync_at = now
        self.socket_client.set_system_time(now_ms, use_object=False)
        self._set_time_sync_notice(drift_ms, note="auto-sync issued")
        self.gui_log.logger.info(
            "Auto time sync issued (device_ms=%s drift_ms=%s)", device_ms, drift_ms
        )

    def _build_status_summary_lines(self, status: Any, max_lines: int = 5) -> List[str]:
        if not isinstance(status, dict):
            return []
        flattened = self._flatten_status(status)
        preferred = [
            "result.telescopeId",
            "result.instrumentState",
            "result.connectionState",
            "result.bootCount",
            "result.currentOperation.state",
            "result.currentOperation.type",
            "result.storage.availableSpace",
            "result.storage.freeSpace",
            "result.camera.temperature",
            "result.sensor.temperature",
            "result.battery.level",
            "result.battery.percent",
            "result.lastError",
        ]
        lines: List[str] = []
        for key in preferred:
            if key in flattened:
                lines.append(f"{key}: {flattened[key]}")
            if len(lines) >= max_lines:
                return lines
        if len(lines) < 3:
            for key in sorted(flattened.keys()):
                if key in preferred:
                    continue
                lines.append(f"{key}: {flattened[key]}")
                if len(lines) >= max_lines:
                    break
        return lines

    def _update_status_summary(self, status: Any) -> None:
        lines = self._build_status_summary_lines(status, max_lines=5)
        if not lines:
            lines = ["(no status yet)"]
        if hasattr(self, "status_summary_var"):
            self.status_summary_var.set("\n".join(lines))
            return
        # Fallback for older widget structure.
        if hasattr(self, "status_summary_text"):
            self.status_summary_text.configure(state="normal")
            self.status_summary_text.delete("1.0", tk.END)
            self.status_summary_text.insert(tk.END, "\n".join(lines))
            self.status_summary_text.configure(state="disabled")

    def _stringify_value(self, value: Any, max_len: int = 200) -> str:
        if isinstance(value, str):
            rendered = value
        else:
            rendered = str(value)
        if len(rendered) > max_len:
            return rendered[: max_len - 12] + "... (truncated)"
        return rendered

    def _update_status_controls(self, status: Any) -> None:
        flattened = self._flatten_status(status)
        if not flattened:
            return

        if not self.socket_device_var.get().strip():
            for key in (
                "result.telescopeId",
                "telescopeId",
                "result.deviceId",
                "deviceId",
            ):
                value = flattened.get(key)
                if value:
                    self.socket_device_var.set(value)
                    break

        for key, value in flattened.items():
            existing = self.status_values.get(key)
            if key in self.status_items:
                item_id = self.status_items[key]
                self.status_tree.item(item_id, values=(key, value))
                if existing is not None and existing != value:
                    self.status_tree.item(item_id, tags=("changed",))
                else:
                    self.status_tree.item(item_id, tags=())
            else:
                item_id = self.status_tree.insert("", tk.END, values=(key, value))
                self.status_items[key] = item_id
            self.status_values[key] = value

    def _is_debug_operation(self, operation_id: str, path: str) -> bool:
        lowered = f"{operation_id} {path}".lower()
        return "debug" in lowered

    def _is_dangerous_path(self, path: str) -> bool:
        lowered = path.lower()
        dangerous = [
            "shutdown",
            "restart",
            "update",
            "delete",
            "openarm",
            "parkarm",
        ]
        return any(token in lowered for token in dangerous)


def main() -> None:
    root = tk.Tk()
    BarnardControlApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
