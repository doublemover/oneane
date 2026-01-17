#!/usr/bin/env python3
"""Extract the Barnard auth key from APK artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Iterable, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "python"))

from vaonis_instruments.auth_key_extractor import ensure_auth_key


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Extract the Barnard auth key from APK artifacts."
    )
    parser.add_argument("--smali", type=Path, help="Path to InstrumentRepository.smali")
    parser.add_argument("--search-root", type=Path, help="Root to search for smali")
    parser.add_argument("--apk", type=Path, help="APK/XAPK to decode with apktool")
    parser.add_argument("--input", type=Path, help="APK/XAPK/ZIP or decoded folder")
    parser.add_argument(
        "--apktool-jar",
        type=Path,
        help="Path to apktool jar (default: tools/apktool_2.9.3.jar)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        help="Output path for the base64 key (default: src/python/.auth_key)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON output",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.smali or args.search_root:
        input_path = args.smali or args.search_root
    else:
        input_path = args.input or args.apk

    try:
        output_path = ensure_auth_key(
            input_path=input_path,
            key_path=args.out,
            apktool_jar=args.apktool_jar,
            prompt=input,
        )
    except Exception as exc:
        if args.json:
            print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=True))
        else:
            print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(
            json.dumps(
                {
                    "ok": True,
                    "outputFile": output_path.name,
                },
                ensure_ascii=True,
            )
        )
    else:
        print("Wrote auth key file.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
