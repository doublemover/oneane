"""Helpers to locate and extract the Barnard auth key from APK artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import base64
from pathlib import Path
import re
import subprocess
import tempfile
from typing import Callable, Iterable, List, Optional, Union
import zipfile

from .logging_utils import find_repo_root


class AuthKeyError(RuntimeError):
    """Raised when auth key extraction fails."""


class AuthKeyNotFound(AuthKeyError):
    """Raised when no auth key can be found."""


class MultipleAuthKeysFound(AuthKeyError):
    """Raised when more than one auth key is detected."""


BASE64_RE = re.compile(r"^[A-Za-z0-9+/]+={0,2}$")
METHOD_RE = re.compile(r"\.method[^\n]*getAuthHeader[^\n]*\n(.*?)\n\.end method", re.S)
STRING_RE = re.compile(r'const-string(?:/jumbo)?\s+v\d+,\s+"([^"]+)"')


@dataclass
class ExtractedKey:
    key: str
    sources: List[Path]


def default_key_path() -> Path:
    return Path(__file__).resolve().parents[1] / ".auth_key"


def default_apktool_jar() -> Path:
    return find_repo_root() / "tools" / "apktool_2.9.3.jar"


def _allowed_roots() -> list[Path]:
    roots = [Path.cwd(), Path.home(), Path(tempfile.gettempdir())]
    roots.append(Path(__file__).resolve().parents[1])
    try:
        roots.append(find_repo_root())
    except Exception:
        pass
    return roots


def _is_within_root(root: Path, target: Path) -> bool:
    try:
        target.relative_to(root)
        return True
    except ValueError:
        return False


def _normalize_safe_path(path: Union[str, Path]) -> Path:
    resolved = Path(path).expanduser().resolve(strict=False)
    for root in _allowed_roots():
        try:
            root_resolved = root.resolve(strict=False)
        except Exception:
            continue
        if _is_within_root(root_resolved, resolved):
            return resolved
    raise AuthKeyError(f"Path outside allowed roots: {resolved}")


def _normalize_optional_path(path: Optional[Union[str, Path]]) -> Optional[Path]:
    if path is None:
        return None
    return _normalize_safe_path(path)


def _decode_base64(value: str) -> Optional[bytes]:
    try:
        return base64.b64decode(value, validate=True)
    except Exception:
        return None


def _extract_candidates(text: str) -> List[str]:
    match = METHOD_RE.search(text)
    segment = match.group(1) if match else text
    candidates: List[str] = []
    for match in STRING_RE.finditer(segment):
        raw = match.group(1).strip()
        if len(raw) < 20 or not BASE64_RE.match(raw):
            continue
        decoded = _decode_base64(raw)
        if decoded is None:
            continue
        if len(decoded) == 64:
            candidates.append(raw)
    return candidates


def _find_smali_files(root: Path) -> List[Path]:
    return sorted(root.rglob("InstrumentRepository.smali"))


def _decode_apk(apk_path: Path, apktool_jar: Path, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        "java",
        "-jar",
        str(apktool_jar),
        "d",
        "-f",
        "-o",
        str(output_dir),
        str(apk_path),
    ]
    subprocess.run(cmd, check=True)
    return output_dir


def _score_apk(path: Path) -> int:
    name = path.name.lower()
    if "base" in name:
        return 0
    if "com.vaonis" in name or "barnard" in name:
        return 1
    return 2


def _expand_zip(zip_path: Path) -> Path:
    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out_dir = find_repo_root() / "temp" / f"zip_extract_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(out_dir)
    return out_dir


def _pick_candidates(root: Path) -> List[Path]:
    preferred = root / "com.vaonis.barnard.zip"
    candidates: List[Path] = []
    if preferred.exists():
        candidates.append(preferred)
    for ext in (".apk", ".xapk", ".zip"):
        for path in root.glob(f"*{ext}"):
            if path not in candidates:
                candidates.append(path)
    return candidates


def _extract_key_from_smali(smali_paths: Iterable[Path]) -> ExtractedKey:
    keys: dict[str, List[Path]] = {}
    for path in smali_paths:
        text = path.read_text(encoding="utf-8", errors="ignore")
        for key in _extract_candidates(text):
            keys.setdefault(key, []).append(path)
    if not keys:
        raise AuthKeyNotFound("No 64-byte base64 key found.")
    if len(keys) > 1:
        details = "\n".join(
            f"{key}: {', '.join(str(p) for p in paths)}" for key, paths in keys.items()
        )
        raise MultipleAuthKeysFound(f"Multiple keys found:\n{details}")
    key, sources = next(iter(keys.items()))
    return ExtractedKey(key=key, sources=sources)


def _prompt_for_path(prompt: Callable[[str], str]) -> Path:
    raw = prompt("Enter path to Barnard APK/XAPK/ZIP or decoded folder: ").strip()
    if not raw:
        raise AuthKeyNotFound("No input provided.")
    path = _normalize_safe_path(Path(raw))
    if not path.exists():
        raise AuthKeyNotFound(f"Path not found: {path}")
    return path


def ensure_auth_key(
    *,
    input_path: Optional[Union[str, Path]] = None,
    key_path: Optional[Union[str, Path]] = None,
    apktool_jar: Optional[Union[str, Path]] = None,
    prompt: Optional[Callable[[str], str]] = None,
) -> Path:
    output_path = _normalize_safe_path(key_path) if key_path else default_key_path()
    output_path = _normalize_safe_path(output_path)
    if output_path.exists() and output_path.read_text(encoding="utf-8").strip():
        return output_path

    resolved_input = _normalize_optional_path(input_path)
    if resolved_input is None:
        candidates = _pick_candidates(find_repo_root())
        if candidates:
            resolved_input = _normalize_safe_path(candidates[0])
        elif prompt is not None:
            resolved_input = _prompt_for_path(prompt)
        else:
            raise AuthKeyNotFound("No input path provided and no archive found.")

    if not resolved_input.exists():
        raise AuthKeyNotFound(f"Input not found: {resolved_input}")

    if resolved_input.is_file() and resolved_input.suffix.lower() == ".smali":
        extracted = _extract_key_from_smali([resolved_input])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(f"{extracted.key}\n", encoding="utf-8")
        return output_path

    search_root: Optional[Path] = None
    if resolved_input.is_dir():
        search_root = resolved_input
    else:
        suffix = resolved_input.suffix.lower()
        if suffix in (".zip", ".xapk"):
            search_root = _expand_zip(resolved_input)
        elif suffix == ".apk":
            search_root = resolved_input
        else:
            raise AuthKeyError(f"Unsupported input: {resolved_input}")

    if search_root is None:
        raise AuthKeyError("Unable to resolve search root for smali files.")

    if search_root.is_file() and search_root.suffix.lower() == ".apk":
        jar = (
            _normalize_safe_path(apktool_jar) if apktool_jar else default_apktool_jar()
        )
        jar = _normalize_safe_path(jar)
        if not jar.exists():
            raise AuthKeyError(f"apktool jar not found: {jar}")
        stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        out_dir = find_repo_root() / "temp" / f"apktool_{stamp}"
        search_root = _decode_apk(search_root, jar, out_dir)

    smali_paths = _find_smali_files(search_root)
    if not smali_paths and search_root.is_dir():
        apks = sorted(search_root.rglob("*.apk"), key=_score_apk)
        for apk_path in apks:
            jar = (
                _normalize_safe_path(apktool_jar)
                if apktool_jar
                else default_apktool_jar()
            )
            jar = _normalize_safe_path(jar)
            if not jar.exists():
                raise AuthKeyError(f"apktool jar not found: {jar}")
            stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            out_dir = find_repo_root() / "temp" / f"apktool_{stamp}"
            decoded = _decode_apk(apk_path, jar, out_dir)
            smali_paths = _find_smali_files(decoded)
            if smali_paths:
                break

    if not smali_paths:
        raise AuthKeyNotFound("No InstrumentRepository.smali files found.")

    extracted = _extract_key_from_smali(smali_paths)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(f"{extracted.key}\n", encoding="utf-8")
    return output_path
