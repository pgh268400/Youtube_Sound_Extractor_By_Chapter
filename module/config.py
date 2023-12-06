# json 설정 파일 생성 & 변수 관리


import json
import os

from type.type import ConfigResult


class Config:
    def __init__(self, settings_file_path: str) -> None:
        try:
            self.settings_file_path = settings_file_path

            # JSON 파일 기본값 지정----------------------------------------------

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
            self.download_folder = "source"  # 다운로드 폴더명
            # -----------------------------------------------------------------

            if os.path.exists(self.settings_file_path):
                # 기본 설정 파일 있으면 불러옴

                with open(self.settings_file_path, "r", encoding="utf-8") as f:
                    settings = json.load(f)

                self.total_offset = settings["total_offset"]
                self.custom_offset = settings["custom_offset"]
                self.thumbnail_folder = settings["thumbnail_folder"]
                self.output_folder = settings["output_folder"]
                self.download_folder = settings["download_folder"]
            else:
                # 기본 설정 파일 없으면 생성
                with open(self.settings_file_path, "w", encoding="utf-8") as f:
                    json.dump(
                        {
                            "total_offset": self.total_offset,
                            "custom_offset": self.custom_offset,
                            "thumbnail_folder": self.thumbnail_folder,
                            "output_folder": self.output_folder,
                            "download_folder": self.download_folder,
                        },
                        f,
                        indent=4,
                    )
        except KeyError as e:
            # json 파일 삭제
            os.remove(self.settings_file_path)
            raise e
        except Exception as e:
            raise e

    def get(self) -> ConfigResult:
        return ConfigResult(
            thumbnail_folder=self.thumbnail_folder,
            output_folder=self.output_folder,
            total_offset=self.total_offset,
            custom_offset=self.custom_offset,
        )
