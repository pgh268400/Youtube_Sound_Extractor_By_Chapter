# json 설정 파일 생성 & 변수 관리


import json
import os

from type.type import ConfigResult


class Config:
    def __init__(self, settings_file_path: str) -> None:
        self.settings_file_path = settings_file_path

        # 아래 변수들은 json 파일에서 불러오면서 바뀌니
        # 직접 수정하지 말고 json에서 수정하자.
        # 값이 지정되어 있는 이유는 전부 기본값을 위해서임.

        # 썸네일 추출시 +- 전체적으로 몇 초 보정할 지 오프셋값
        self.total_offset = 0

        # 특정 순번의 썸네일에만 오프셋을 따로 줄 수도 있음
        self.custom_offset = {
            # "1": 4 # 1번 챕터에만 +N초 오프셋을 줌 (total_offset과 합산됨)
            # 2: -5,
            # 3: -8,
            # 4: 7
        }

        self.thumbnail_folder = "thumbnails"  # 썸네일 폴더명
        self.output_folder = "output"  # 최종 결과물 폴더명

        if os.path.exists(self.settings_file_path):
            # 기본 설정 파일 있으면 불러옴
            with open(self.settings_file_path, "r", encoding="utf-8") as f:
                settings = json.load(f)
            self.total_offset = settings["total_offset"]
            self.custom_offset = settings["custom_offset"]
            self.thumbnail_folder = settings["thumbnail_folder"]
            self.output_folder = settings["output_folder"]
        else:
            # 기본 설정 파일 없으면 생성
            with open(self.settings_file_path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "total_offset": self.total_offset,
                        "custom_offset": self.custom_offset,
                        "thumbnail_folder": self.thumbnail_folder,
                        "output_folder": self.output_folder,
                    },
                    f,
                    indent=4,
                )

    def get(self) -> ConfigResult:
        return ConfigResult(
            thumbnail_folder=self.thumbnail_folder,
            output_folder=self.output_folder,
            total_offset=self.total_offset,
            custom_offset=self.custom_offset,
        )
