from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(slots=True)
class General:
    audio_filename: str = ""
    audio_lead_in: int = 0
    preview_time: int = 0
    countdown: int = 0
    sample_set: int = 2
    stack_leniency: float = 0.7
    mode: int = 0
    letterbox_in_breaks: bool = False
    special_style: bool = False
    widescreen_storyboard: bool = False
    epilepsy_warning: bool = False
    samples_match_playback_rate: bool = False
    extras: Dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class Editor:
    bookmarks: List[int] = field(default_factory=list)
    distance_spacing: float = 1.0
    beat_divisor: int = 4
    grid_size: int = 4
    timeline_zoom: float = 1.0
    extras: Dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class Metadata:
    title: str = ""
    title_unicode: str = ""
    artist: str = ""
    artist_unicode: str = ""
    creator: str = ""
    version: str = ""
    source: str = ""
    tags: List[str] = field(default_factory=list)
    beatmap_id: int = -1
    beatmap_set_id: int = -1
    audio_filename: str = ""
    preview_time: int = 0
    extras: Dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class Difficulty:
    hp_drain_rate: float = 5.0
    circle_size: float = 5.0
    overall_difficulty: float = 5.0
    approach_rate: float = 5.0
    slider_multiplier: float = 1.0
    slider_tick_rate: float = 1.0
    extras: Dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class TimingPoint:
    offset: float = 0.0
    beat_length: float = 0.0
    meter: int = 4
    sample_set: int = 1
    sample_index: int = 0
    volume: int = 100
    uninherited: int = 0
    effects: int = 0


@dataclass(slots=True)
class HitObject:
    x: int = 0
    y: int = 0
    time: int = 0
    type: int = 0
    hitsound: int = 0
    extras: List[str] = field(default_factory=list)


@dataclass(slots=True)
class EventLine:
    values: List[str] = field(default_factory=list)


@dataclass(slots=True)
class Colour:
    name: str = ""
    r: int = 255
    g: int = 255
    b: int = 255


@dataclass(slots=True)
class Colours:
    combo_colours: List[Colour] = field(default_factory=list)
    slider_border: Optional[Colour] = None
    slider_track_override: Optional[Colour] = None
    extras: Dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class UnknownSection:
    name: str = ""
    lines: List[str] = field(default_factory=list)
    key_values: Dict[str, List[str]] = field(default_factory=dict)


@dataclass(slots=True)
class Beatmap:
    general: General = field(default_factory=General)
    editor: Editor = field(default_factory=Editor)
    metadata: Metadata = field(default_factory=Metadata)
    difficulty: Difficulty = field(default_factory=Difficulty)
    events: List[EventLine] = field(default_factory=list)
    timing_points: List[TimingPoint] = field(default_factory=list)
    colours: Colours = field(default_factory=Colours)
    hit_objects: List[HitObject] = field(default_factory=list)

    variables: Dict[str, str] = field(default_factory=dict)
    raw_sections: Dict[str, UnknownSection] = field(default_factory=dict)

    raw_lines: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)