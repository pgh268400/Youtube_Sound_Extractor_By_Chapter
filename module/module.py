from datetime import datetime, timedelta
import re
import subprocess
import mutagen
import requests
from type.type import BaseChapter, RangedChapter
from mutagen.mp4 import MP4
from yt_dlp import YoutubeDL

"""
터미널 컬러 텍스트 일반 텍스트로 변경
Ansi color code 제거

Reference:
    https://118k.tistory.com/1179
    https://stackoverflow.com/questions/14693701/how-can-i-remove-the-ansi-escape-sequences-from-a-string-in-python
"""


def escape_ansi_color_pattern(ansi_text: str) -> str:
    # 7-bit C1 ANSI sequences
    ansi_escape = re.compile(
        r"""
        \x1B  # ESC
        (?:   # 7-bit C1 Fe (except CSI)
            [@-Z\\-_]
        |     # or [ for CSI, followed by a control sequence
            \[
            [0-?]*  # Parameter bytes
            [ -/]*  # Intermediate bytes
            [@-~]   # Final byte
        )
    """,
        re.VERBOSE,
    )
    result = ansi_escape.sub("", ansi_text)
    return result


# if __name__ == "__main__":
#     print(convert_to_seconds("1:30:00"))
#     print(convert_to_seconds("30:00"))
#     print(convert_to_seconds("30"))
