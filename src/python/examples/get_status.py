import argparse
import json

from vaonis_instruments import VaonisHTTPClient
from vaonis_instruments.logging_utils import format_payload, setup_logging


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch instrument status.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    args = parser.parse_args()

    log = setup_logging("http_example", also_console=not args.json)
    client = VaonisHTTPClient(logger=log.logger)

    try:
        status = client.get_status()
        log.logger.info("Status response received")
        if args.json:
            print(json.dumps(status, ensure_ascii=True))
        else:
            print(format_payload(status, color=True))
    except Exception as exc:
        log.logger.exception("Failed to get status: %s", exc)
        if args.json:
            print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=True))
            return 1
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
