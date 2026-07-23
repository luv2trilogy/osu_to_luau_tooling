# osu_to_luau_tooling

a simple converter for .osu beatmaps to JSON or Luau.

## command line usage

convert a file:

```powershell
py main.py convert sample.osu output.json
```

convert to LUAU:

```powershell
py main.py convert sample.osu output.lua --format luau
```

interactive mode:

```powershell
py main.py interactive
```

## desktop UI

run:

```powershell
py ui.py
```

this opens a very small window with:
- a file picker
- a selected-file label
- output format choices
- a convert button
