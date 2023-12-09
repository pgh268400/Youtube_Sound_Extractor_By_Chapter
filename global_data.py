# 전역 변수를저장하는 곳 (Read-Only)
from typing import Final
from module.config import Config

title: Final[str] = "Youtube Chapter Converter"
theme_path: Final[str] = "theme.css"
icon_path: Final[str] = "./icon/icon.png"

# 설정 파일 객체는 싱글톤으로 전역으로 사용한다.
config = Config("./settings.json")
