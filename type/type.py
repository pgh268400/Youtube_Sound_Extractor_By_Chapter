from dataclasses import dataclass


@dataclass
class BaseChapter:
    title: str
    timeline: str


@dataclass
class RangedChapter:
    title: str
    start_time: float
    end_time: float


@dataclass
class ConfigResult:
    total_offset: int
    custom_offset: dict
    thumbnail_folder: str
    output_folder: str
    download_folder: str
