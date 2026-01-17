"""Example stub: starting an observation.

This uses the local auth key extractor to generate a valid Authorization header.
"""

import argparse
import json

from vaonis_instruments import AuthContext, VaonisHTTPClient, build_authorization_header
from vaonis_instruments import ensure_auth_key
from vaonis_instruments.logging_utils import format_payload, setup_logging


def main() -> int:
    parser = argparse.ArgumentParser(description="Start an observation (example).")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    args = parser.parse_args()

    log = setup_logging("start_observation", also_console=not args.json)
    client = VaonisHTTPClient(logger=log.logger)

    ensure_auth_key(prompt=input)
    status = client.get_status()
    ctx = AuthContext(
        challenge=status["result"]["challenge"],
        telescope_id=status["result"]["telescopeId"],
        boot_count=status["result"]["bootCount"],
    )
    auth = build_authorization_header(ctx)

    body = {
        "objectName": "M42",
        "objectId": "",
        "objectType": "NGC",
        "targetType": "DEEP_SKY",
        "store": "RAW",
        # The rest of fields in StartObservationBody are optional per the app model.
    }

    try:
        response = client.start_observation(auth, body)
        log.logger.info("Start observation response received")
        if args.json:
            print(json.dumps(response, ensure_ascii=True))
        else:
            print(format_payload(response, color=True))
    except Exception as exc:
        log.logger.exception("Start observation failed: %s", exc)
        if args.json:
            print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=True))
            return 1
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
