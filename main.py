from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional, TextIO

from converter import ConversionPipeline
from converter.parser import parse_osu


def resolve_input_text(input_path: Optional[str] = None, use_stdin: bool = False, stdin_stream: Optional[TextIO] = None) -> str:
    if use_stdin:
        stream = stdin_stream or sys.stdin
        return stream.read()

    if not input_path:
        raise ValueError("An input path or stdin input is required")

    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    return path.read_text(encoding="utf-8")


def build_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert .osu beatmaps to JSON or Luau")
    subparsers = parser.add_subparsers(dest="command")

    convert_parser = subparsers.add_parser("convert", help="Convert an .osu file to JSON or Luau")
    convert_parser.add_argument("input", nargs="?", help="Path to the .osu file to convert")
    convert_parser.add_argument("output", nargs="?", help="Path to write the converted output")
    convert_parser.add_argument("--format", choices=["json", "luau", "both"], default="json")
    convert_parser.add_argument("--stdin", action="store_true", help="Read .osu content from standard input")

    subparsers.add_parser("interactive", help="Start a very basic interactive prompt")

    return parser


def run_interactive_mode() -> int:
    print("osu -> Luau/JSON converter")
    print("Type 'quit' to exit")

    while True:
        try:
            path = input("Enter .osu file path: ").strip()
        except EOFError:
            print()
            return 0

        if path.lower() in {"quit", "exit"}:
            return 0

        try:
            content = resolve_input_text(path)
        except Exception as exc:
            print(f"Error: {exc}")
            continue

        format_name = input("Output format [json/luau/both]: ").strip().lower() or "json"
        if format_name not in {"json", "luau", "both"}:
            print("Unsupported format, defaulting to json")
            format_name = "json"

        beatmap = parse_osu(content)
        if beatmap.warnings:
            for warning in beatmap.warnings:
                print(f"Warning: {warning}")

        pipeline = ConversionPipeline()
        if format_name == "json":
            print(pipeline.json_serializer(beatmap))
        elif format_name == "luau":
            print(pipeline.luau_serializer(beatmap))
        else:
            print(pipeline.json_serializer(beatmap))
            print()
            print(pipeline.luau_serializer(beatmap))


def _write_conversion_output(output_path: str, output_format: str, json_text: str, luau_text: str) -> None:
    """Write conversion output to disk, splitting 'both' into two real files."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    if output_format == "both":
        json_path = out.with_suffix(".json")
        luau_path = out.with_suffix(".lua")
        json_path.write_text(json_text, encoding="utf-8")
        luau_path.write_text(luau_text, encoding="utf-8")
        print(f"Wrote {json_path}")
        print(f"Wrote {luau_path}")
    else:
        out.write_text(json_text if output_format == "json" else luau_text, encoding="utf-8")


def handle_conversion(input_path: Optional[str], output_path: Optional[str], output_format: str, use_stdin: bool = False) -> int:
    try:
        content = resolve_input_text(input_path, use_stdin=use_stdin)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    pipeline = ConversionPipeline()
    beatmap = parse_osu(content)

    if beatmap.warnings:
        for warning in beatmap.warnings:
            print(f"Warning: {warning}", file=sys.stderr)

    if output_format == "both":
        json_text = pipeline.json_serializer(beatmap)
        luau_text = pipeline.luau_serializer(beatmap)
    elif output_format == "json":
        json_text, luau_text = pipeline.json_serializer(beatmap), ""
    else:
        json_text, luau_text = "", pipeline.luau_serializer(beatmap)

    if output_path:
        _write_conversion_output(output_path, output_format, json_text, luau_text)
    else:
        if output_format == "both":
            print(json_text)
            print()
            print(luau_text)
        else:
            print(json_text or luau_text)

    return 0


def main() -> int:
    parser = build_cli()
    args = parser.parse_args()

    if args.command == "convert":
        return handle_conversion(args.input, args.output, args.format, use_stdin=args.stdin)

    if args.command == "interactive":
        return run_interactive_mode()

    parser.print_help()
    return 1


def run_drag_and_drop() -> int:
    if len(sys.argv) < 2:
        print("Drop an .osu file onto this script to convert it.")
        return 1

    dropped_path = " ".join(sys.argv[1:]).strip().strip('"')
    if not dropped_path:
        return 1

    input_path = Path(dropped_path)
    if not input_path.exists():
        print(f"File not found: {input_path}", file=sys.stderr)
        return 2

    output_path = input_path.with_suffix(".json")
    return handle_conversion(str(input_path), str(output_path), "json")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() == "drop":
        sys.exit(run_drag_and_drop())
    sys.exit(main())