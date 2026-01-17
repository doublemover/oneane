from __future__ import annotations

from typing import Any

import pytest

from vaonis_instruments import gui_app


def test_json_helpers() -> None:
    assert gui_app._safe_json_load("") is None
    assert gui_app._safe_json_load('{"a": 1}') == {"a": 1}

    class Unserializable:
        def __str__(self) -> str:
            return "fallback"

    assert gui_app._format_json({"a": 1}).strip().startswith("{")
    assert gui_app._format_json(Unserializable()) == "fallback"
    assert gui_app._looks_like_url("http://example") is True
    assert gui_app._looks_like_url("/path") is False


def test_image_extension_and_urls() -> None:
    assert gui_app._image_extension(b"\xff\xd8\xff", None) == ".jpg"
    assert gui_app._image_extension(b"\x89PNG\r\n\x1a\n", None) == ".png"
    assert gui_app._image_extension(b"GIF89a", None) == ".gif"
    assert gui_app._image_extension(b"BM", None) == ".bmp"
    assert gui_app._image_extension(b"II*\x00", None) == ".tiff"
    assert gui_app._image_extension(b"RIFFxxxxWEBP", None) == ".webp"
    assert gui_app._image_extension(b"???", None) == ".bin"
    assert gui_app._image_extension(b"", "image/jpeg") == ".jpg"

    payload: Any = {
        "previewUrl": "/preview.jpg",
        "nested": {"thumbnailUrl": "/thumb.png"},
        "list": [{"imagePath": "/image.bin"}],
    }
    urls = gui_app._find_image_urls(payload)
    assert "/preview.jpg" in urls
    assert "/thumb.png" in urls
    assert "/image.bin" in urls
