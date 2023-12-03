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