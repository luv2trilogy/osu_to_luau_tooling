from __future__ import annotations

from typing import Any, Dict, Optional

from .parser import parse_osu
from .serializers import serialize_to_json, serialize_to_luau


class ConversionPipeline:
    """Coordinates parsing and serialization for beatmap conversion."""

    def __init__(self, parser=parse_osu, json_serializer=serialize_to_json, luau_serializer=serialize_to_luau):
        self.parser = parser
        self.json_serializer = json_serializer
        self.luau_serializer = luau_serializer

    def convert(self, text: str, output_format: str = "json") -> str:
        beatmap = self.parser(text)
        if output_format == "json":
            return self.json_serializer(beatmap)
        if output_format == "luau":
            return self.luau_serializer(beatmap)
        if output_format == "both":
            return "\n\n".join([self.json_serializer(beatmap), self.luau_serializer(beatmap)])
        raise ValueError(f"Unsupported output format: {output_format}")
