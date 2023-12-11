import os
import re
import sys
from PySide6.QtWidgets import QMainWindow

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


def resource_path(relative_path: str) -> str:
    try:
        # PyInstaller에 의해 임시폴더에서 실행될 경우 임시폴더로 접근하는 함수
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
