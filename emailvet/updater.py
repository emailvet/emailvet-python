from __future__ import annotations

import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.request import Request, urlopen

from .rules import (
    _downloaded_rules_path,
    clear_rules_cache,
    rules_version,
    validate_rules,
)


DEFAULT_RULES_URL = None


def _get_update_url(url: str | None) -> str:
    if url:
        return url

    env_url = os.environ.get("EMAILVET_RULES_URL")

    if env_url:
        return env_url

    if DEFAULT_RULES_URL:
        return DEFAULT_RULES_URL

    raise ValueError(
        "No rules update URL configured. Pass a URL to update_rules() "
        "or set EMAILVET_RULES_URL."
    )


def update_rules(
    url: str | None = None,
    *,
    timeout: float = 10.0,
) -> dict:
    update_url = _get_update_url(url)

    request = Request(
        update_url,
        headers={
            "User-Agent": "emailvet/0.1.0",
            "Accept": "application/json",
        },
    )

    with urlopen(request, timeout=timeout) as response:
        raw = response.read()

    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Downloaded rules are not valid UTF-8 JSON") from exc

    validate_rules(data)

    current_version = rules_version()
    new_version = data["rules_version"]

    destination = _downloaded_rules_path()
    destination.parent.mkdir(parents=True, exist_ok=True)

    temp_path: Path | None = None

    try:
        with NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=destination.parent,
            prefix="providers.",
            suffix=".tmp",
            delete=False,
        ) as temp_file:
            json.dump(data, temp_file, indent=2, ensure_ascii=False)
            temp_file.write("\n")
            temp_file.flush()
            os.fsync(temp_file.fileno())
            temp_path = Path(temp_file.name)

        os.replace(temp_path, destination)
        temp_path = None
    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()

    clear_rules_cache()

    return {
        "previous_version": current_version,
        "version": new_version,
        "updated": new_version != current_version,
        "path": str(destination),
    }
