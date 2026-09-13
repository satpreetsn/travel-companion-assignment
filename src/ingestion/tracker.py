import hashlib
import json
from pathlib import Path


MANIFEST_PATH = Path("ingestion_state/manifest.json")


def calculate_file_hash(file_path: str) -> str:
    """Calculate SHA-256 hash for a file."""

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        while chunk := file.read(1024 * 1024):
            sha256.update(chunk)

    return sha256.hexdigest()


def load_manifest() -> dict:
    """Load ingestion state from disk."""

    if not MANIFEST_PATH.exists():
        return {}

    with open(MANIFEST_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def save_manifest(manifest: dict) -> None:
    """Save ingestion state to disk."""

    MANIFEST_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(MANIFEST_PATH, "w", encoding="utf-8") as file:
        json.dump(
            manifest,
            file,
            indent=2
        )