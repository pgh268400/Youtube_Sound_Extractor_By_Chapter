# 전역 변수를저장하는 곳 (Read-Only)
from typing import Final
from module.config import Config
from module.module import resource_path

title: Final[str] = "Youtube Chapter Converter"
theme_path: Final[str] = resource_path("theme.css")
icon_path: Final[str] = resource_path("./icon/icon.png")

print(f"theme_path: {theme_path}")
print(f"icon_path: {icon_path}")

# 설정 파일 객체는 싱글톤으로 전역으로 사용한다.
config = Config("./settings.json")
