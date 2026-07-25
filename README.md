# osu_to_luau_tooling

a simple converter for .osu beatmaps to JSON or Luau.

parses General, Editor, Metadata, Difficulty, Events, TimingPoints, Colours, and HitObjects into typed data. anything else is kept as raw unknown sections so nothing gets lost on conversion.

## command line usage

convert a file:

py main.py convert sample.osu output.json

convert to LUAU:

py main.py convert sample.osu output.lua --format luau

convert to both formats:

py main.py convert sample.osu output --format both

read from stdin:

py main.py convert --stdin < sample.osu

interactive mode:

py main.py interactive

## drag and drop

drop an .osu file onto main.py (or run `main.py drop <file>`) to convert it straight to JSON next to the original file.

## desktop UI

run:

py ui.py

this opens a window with:

- a file picker with drag-and-drop support (via tkinterdnd2)
- output format selection (JSON / Luau / Both)
- an output folder picker
- a live output preview
- a convert button

## install

pip install -r requirements.txt

or, as a package:

pip install -e .

this exposes an `osu2luau` command pointing at `main:main`.

## project layout

- `converter/` — parsing and serialization
  - `models.py` — dataclasses for General, Editor, Metadata, Difficulty, TimingPoint, HitObject, Colours, etc.
  - `parser.py` — turns raw .osu text into a `Beatmap`
  - `serializers.py` — `Beatmap` → JSON or Luau table
  - `pipeline.py` — `ConversionPipeline`, ties parsing + serialization together
- `main.py` — CLI entry point
- `ui.py` — desktop UI entry point
- `examples/` — sample .osu files
- `tests/` — test suite

## requirements

- Python 3.11+
- `customtkinter`, `tkinterdnd2` (for the desktop UI)