from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any

from .models import Beatmap


def _to_primitive(value: Any) -> Any:
    if is_dataclass(value):
        return {key: _to_primitive(item) for key, item in asdict(value).items()}
    if isinstance(value, dict):
        return {str(key): _to_primitive(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_to_primitive(item) for item in value]
    if isinstance(value, tuple):
        return [_to_primitive(item) for item in value]
    return value


def serialize_to_json(beatmap: Beatmap) -> str:
    return json.dumps(_to_primitive(beatmap), indent=2, ensure_ascii=False)


def _luau_value(value: Any, indent: int = 0) -> str:
    prefix = " " * indent

    if isinstance(value, dict):
        if not value:
            return "{}"

        lines = ["{"]
        for key in sorted(value.keys(), key=str):
            item = value[key]
            lines.append(f'{prefix}  [{json.dumps(str(key))}] = {_luau_value(item, indent + 2)},')
        lines.append(f"{prefix}}}")
        return "\n".join(lines)

    if isinstance(value, list):
        if not value:
            return "{}"
        items = ", ".join(_luau_value(item, indent + 2) for item in value)
        return "{ " + items + " }"

    if isinstance(value, bool):
        return "true" if value else "false"

    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)

    if value is None:
        return "nil"

    return str(value)


def serialize_to_luau(beatmap: Beatmap) -> str:
    payload = _luau_value(_to_primitive(beatmap))
    return f"return {payload}"