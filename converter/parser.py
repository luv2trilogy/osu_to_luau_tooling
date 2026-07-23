from __future__ import annotations

import csv
from typing import Dict, List, Optional

from .models import (
    Beatmap,
    Colour,
    Editor,
    EventLine,
    General,
    HitObject,
    Metadata,
    TimingPoint,
    UnknownSection,
)


STANDARD_SECTIONS = {
    "General",
    "Editor",
    "Metadata",
    "Difficulty",
    "Events",
    "TimingPoints",
    "Colours",
    "Colors",
    "HitObjects",
    "Variables",
}


def _parse_int(value: str, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _parse_float(value: str, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _parse_bool(value: str, default: bool = False) -> bool:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes"}:
        return True
    if normalized in {"0", "false", "no"}:
        return False
    return default


def _split_csv_line(line: str) -> List[str]:
    reader = csv.reader([line], skipinitialspace=False)
    return [item.strip() for item in next(reader)]


def _parse_colour_value(value: str) -> Optional[Colour]:
    parts = [part.strip() for part in value.split(",")]
    if len(parts) < 3:
        return None

    return Colour(
        r=_parse_int(parts[0], 255),
        g=_parse_int(parts[1], 255),
        b=_parse_int(parts[2], 255),
    )


def parse_osu(text: str, *, preserve_raw_lines: bool = False) -> Beatmap:
    """
    Parse a subset of .osu content into a structured beatmap model.

    - Standard sections are mapped into typed dataclasses.
    - Unknown sections are preserved in Beatmap.raw_sections.
    - If preserve_raw_lines=True, the original file lines are kept in Beatmap.raw_lines.
    """
    beatmap = Beatmap()
    current_section = ""
    current_unknown: Optional[UnknownSection] = None

    lines = text.splitlines()
    if preserve_raw_lines:
        beatmap.raw_lines = list(lines)

    for raw_line in lines:
        line = raw_line.strip()

        if not line or line.startswith("//"):
            continue

        if line.startswith("[") and line.endswith("]"):
            current_section = line[1:-1].strip()
            current_unknown = None

            if current_section not in STANDARD_SECTIONS:
                current_unknown = beatmap.raw_sections.setdefault(
                    current_section,
                    UnknownSection(name=current_section),
                )
            continue

        if not current_section:
            continue

        if current_section == "TimingPoints":
            values = _split_csv_line(line)
            if len(values) >= 2:
                beatmap.timing_points.append(
                    TimingPoint(
                        offset=_parse_float(values[0], 0.0),
                        beat_length=_parse_float(values[1], 0.0),
                        meter=_parse_int(values[2], 4) if len(values) > 2 else 4,
                        sample_set=_parse_int(values[3], 1) if len(values) > 3 else 1,
                        sample_index=_parse_int(values[4], 0) if len(values) > 4 else 0,
                        volume=_parse_int(values[5], 100) if len(values) > 5 else 100,
                        uninherited=_parse_int(values[6], 0) if len(values) > 6 else 0,
                        effects=_parse_int(values[7], 0) if len(values) > 7 else 0,
                    )
                )
            continue

        if current_section == "HitObjects":
            values = _split_csv_line(line)
            if len(values) >= 5:
                beatmap.hit_objects.append(
                    HitObject(
                        x=_parse_int(values[0], 0),
                        y=_parse_int(values[1], 0),
                        time=_parse_int(values[2], 0),
                        type=_parse_int(values[3], 0),
                        hitsound=_parse_int(values[4], 0),
                        extras=values[5:],
                    )
                )
            continue

        if current_section == "Events":
            values = _split_csv_line(line)
            beatmap.events.append(EventLine(values=values))
            continue

        if current_section == "Variables":
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            beatmap.variables[key.strip()] = value.strip()
            continue

        if current_section in {"Colours", "Colors"}:
            if ":" not in line:
                continue

            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            colour = _parse_colour_value(value)

            if colour is None:
                beatmap.colours.extras[key] = value
                continue

            colour.name = key

            lowered = key.lower()
            if lowered.startswith("combo"):
                beatmap.colours.combo_colours.append(colour)
            elif lowered == "sliderborder":
                beatmap.colours.slider_border = colour
            elif lowered == "slidertrackoverride":
                beatmap.colours.slider_track_override = colour
            else:
                beatmap.colours.extras[key] = value
            continue

        if ":" not in line:
            if current_unknown is not None:
                current_unknown.lines.append(raw_line)
            continue

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()

        if current_unknown is not None:
            current_unknown.lines.append(raw_line)
            current_unknown.key_values.setdefault(key, []).append(value)
            continue

        if current_section == "General":
            if key == "AudioFilename":
                beatmap.general.audio_filename = value
            elif key == "AudioLeadIn":
                beatmap.general.audio_lead_in = _parse_int(value, beatmap.general.audio_lead_in)
            elif key == "PreviewTime":
                beatmap.general.preview_time = _parse_int(value, beatmap.general.preview_time)
            elif key == "Countdown":
                beatmap.general.countdown = _parse_int(value, beatmap.general.countdown)
            elif key == "SampleSet":
                beatmap.general.sample_set = _parse_int(value, beatmap.general.sample_set)
            elif key == "StackLeniency":
                beatmap.general.stack_leniency = _parse_float(value, beatmap.general.stack_leniency)
            elif key == "Mode":
                beatmap.general.mode = _parse_int(value, beatmap.general.mode)
            elif key == "LetterboxInBreaks":
                beatmap.general.letterbox_in_breaks = _parse_bool(value, beatmap.general.letterbox_in_breaks)
            elif key == "SpecialStyle":
                beatmap.general.special_style = _parse_bool(value, beatmap.general.special_style)
            elif key == "WidescreenStoryboard":
                beatmap.general.widescreen_storyboard = _parse_bool(value, beatmap.general.widescreen_storyboard)
            elif key == "EpilepsyWarning":
                beatmap.general.epilepsy_warning = _parse_bool(value, beatmap.general.epilepsy_warning)
            elif key == "SamplesMatchPlaybackRate":
                beatmap.general.samples_match_playback_rate = _parse_bool(
                    value, beatmap.general.samples_match_playback_rate
                )
            else:
                beatmap.general.extras[key] = value

        elif current_section == "Editor":
            if key == "Bookmarks":
                beatmap.editor.bookmarks = [
                    _parse_int(item, 0) for item in value.split(",") if item.strip()
                ]
            elif key == "DistanceSpacing":
                beatmap.editor.distance_spacing = _parse_float(value, beatmap.editor.distance_spacing)
            elif key == "BeatDivisor":
                beatmap.editor.beat_divisor = _parse_int(value, beatmap.editor.beat_divisor)
            elif key == "GridSize":
                beatmap.editor.grid_size = _parse_int(value, beatmap.editor.grid_size)
            elif key == "TimelineZoom":
                beatmap.editor.timeline_zoom = _parse_float(value, beatmap.editor.timeline_zoom)
            else:
                beatmap.editor.extras[key] = value

        elif current_section == "Metadata":
            if key == "Title":
                beatmap.metadata.title = value
            elif key == "TitleUnicode":
                beatmap.metadata.title_unicode = value
            elif key == "Artist":
                beatmap.metadata.artist = value
            elif key == "ArtistUnicode":
                beatmap.metadata.artist_unicode = value
            elif key == "Creator":
                beatmap.metadata.creator = value
            elif key == "Version":
                beatmap.metadata.version = value
            elif key == "Source":
                beatmap.metadata.source = value
            elif key == "Tags":
                beatmap.metadata.tags = [item for item in value.split(" ") if item.strip()]
            elif key == "BeatmapID":
                beatmap.metadata.beatmap_id = _parse_int(value, beatmap.metadata.beatmap_id)
            elif key == "BeatmapSetID":
                beatmap.metadata.beatmap_set_id = _parse_int(value, beatmap.metadata.beatmap_set_id)
            elif key == "AudioFilename":
                beatmap.metadata.audio_filename = value
            elif key == "PreviewTime":
                beatmap.metadata.preview_time = _parse_int(value, beatmap.metadata.preview_time)
            else:
                beatmap.metadata.extras[key] = value

        elif current_section == "Difficulty":
            if key == "HPDrainRate":
                beatmap.difficulty.hp_drain_rate = _parse_float(value, beatmap.difficulty.hp_drain_rate)
            elif key == "CircleSize":
                beatmap.difficulty.circle_size = _parse_float(value, beatmap.difficulty.circle_size)
            elif key == "OverallDifficulty":
                beatmap.difficulty.overall_difficulty = _parse_float(value, beatmap.difficulty.overall_difficulty)
            elif key == "ApproachRate":
                beatmap.difficulty.approach_rate = _parse_float(value, beatmap.difficulty.approach_rate)
            elif key == "SliderMultiplier":
                beatmap.difficulty.slider_multiplier = _parse_float(value, beatmap.difficulty.slider_multiplier)
            elif key == "SliderTickRate":
                beatmap.difficulty.slider_tick_rate = _parse_float(value, beatmap.difficulty.slider_tick_rate)
            else:
                beatmap.difficulty.extras[key] = value

        else:
            if current_unknown is None:
                current_unknown = beatmap.raw_sections.setdefault(
                    current_section,
                    UnknownSection(name=current_section),
                )
            current_unknown.lines.append(raw_line)
            current_unknown.key_values.setdefault(key, []).append(value)

    return beatmap