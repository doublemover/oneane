from vaonis_instruments import logging_utils


def test_format_payload_dict_sorted() -> None:
    payload = {"b": 1, "a": 2}
    rendered = logging_utils.format_payload(payload)
    assert '"a": 2' in rendered
    assert '"b": 1' in rendered


def test_format_payload_bytes() -> None:
    rendered = logging_utils.format_payload(b"abc")
    assert rendered == "<3 bytes>"


def test_format_payload_colorize() -> None:
    rendered = logging_utils.format_payload({"key": True}, color=True)
    assert logging_utils.ANSI_BLUE in rendered
    assert logging_utils.ANSI_MAGENTA in rendered


def test_format_payload_truncation() -> None:
    rendered = logging_utils.format_payload("x" * 100, max_len=20)
    assert rendered.endswith("... (truncated)")
