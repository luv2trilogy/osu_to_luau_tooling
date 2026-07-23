from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional, TextIO

from converter import ConversionPipeline


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
    convert_parser.add_argument("input", help="Path to the .osu file to convert")
    convert_parser.add_argument("output", nargs="?", help="Path to write the converted output")
    convert_parser.add_argument("--format", choices=["json", "luau", "both"], default="json")
    convert_parser.add_argument("--stdin", action="store_true", help="Read .osu content from standard input")

    interactive_parser = subparsers.add_parser("interactive", help="Start a very basic interactive prompt")

    parser.add_argument("input", nargs="?", help="Legacy positional input path")
    parser.add_argument("output", nargs="?", help="Legacy positional output path")
    parser.add_argument("--format", choices=["json", "luau", "both"], default="json")
    parser.add_argument("--output", help="Optional path to write the converted output")
    parser.add_argument("--stdin", action="store_true", help="Read .osu content from standard input")
    parser.add_argument("--interactive", action="store_true", help="Start a very basic interactive prompt")
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

        pipeline = ConversionPipeline()
        result = pipeline.convert(content, output_format=format_name)
        print(result)


def handle_conversion(input_path: Optional[str], output_path: Optional[str], output_format: str, use_stdin: bool = False) -> int:
    try:
        content = resolve_input_text(input_path, use_stdin=use_stdin)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    pipeline = ConversionPipeline()
    result = pipeline.convert(content, output_format=output_format)

    if output_path:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(result, encoding="utf-8")
    else:
        print(result)

    return 0


def main() -> int:
    parser = build_cli()
    args = parser.parse_args()

    if args.command == "convert":
        return handle_conversion(args.input, args.output, args.format, use_stdin=args.stdin)

    if args.command == "interactive" or args.interactive:
        return run_interactive_mode()

    if args.input and not args.output and not args.stdin:
        return handle_conversion(args.input, None, args.format)

    if not args.input and not args.stdin:
        parser.print_help()
        return 1

    output_path = args.output if args.output is not None else None
    return handle_conversion(args.input, output_path, args.format, use_stdin=args.stdin)


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


if __name__ == "__main__":
    main()
