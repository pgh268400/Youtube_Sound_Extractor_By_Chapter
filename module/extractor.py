# 유튜브 다운로드, 챕터 파싱, 썸네일 추출 등 다양한 기능을 제공하는 Class (설계도)
# 해당 프로그램은 이 객체에 의존하여 대부분의 기능을 수행한다.


from concurrent.futures import ALL_COMPLETED, wait
from datetime import datetime, timedelta
import multiprocessing
import os
import re
import subprocess
import mutagen
import mutagen.mp4
from mutagen.mp4 import MP4
from natsort import natsorted
from yt_dlp import YoutubeDL
import concurrent
import concurrent.futures
import yt_dlp

from type.type import BaseChapter, RangedChapter
from global_data import config


# 커스텀 예외(=에러)
class FailtoGetInfo(Exception):
    def __init__(self, message="유튜브 정보를 가져오는데 실패했습니다.") -> None:
        self.message = message
        super().__init__(self.message)


class YoutubeExtractor:
    # 생성자
    def __init__(self, youtube_url: str) -> None:
        try:
            self.__url = youtube_url
            self.__info = self.get_youtube_info(self.__url)  # 유튜브 정보 가져오기

            # filename_remover => 파일명에 사용할 수 없는 문자 비슷한 유니코드 문자로 치환
            self.__title: str = self.__filename_remover(self.__info["title"])  # 영상 제목
            self.__duration: str = self.__info["duration_string"]  # 영상 길이
            self.__chapters = self.__info[
                "chapters"
            ]  # 영상 챕터 (영상에 자체적으로 있는 경우만, 없으면 None)

            self.__is_already_chapter = False  # 챕터가 있는지 여부
            if not self.__chapters:
                self.__is_already_chapter = False
            else:
                self.__is_already_chapter = True

            # 설정 파일에서 설정값을 가져옴
            self.__thumbnail_folder: str = config.get().thumbnail_folder
            self.__output_folder: str = config.get().output_folder
            self.__custom_offset = config.get().custom_offset
            self.__total_offset = config.get().total_offset
            self.__download_folder = config.get().download_folder

            """
                mp4로 받는 경우
                    mp4는 fragment(파편화)가 있어서 조각 조각 받아야 해서 다운로드가 느리지만
                    대신에 음원 추출은 그냥 영상에서 추출하면 하면 되서 기다리는 시간이 제로임.
                webp로 받는 경우
                    mp4 대비 용량이 작고, fragment(파편화) 가 없어서 다운로드가 빨리 끝나나
                    음원 추출은 재 인코딩 해야 해서 영상 길이만큼 시간이 걸림.
                결론:
                다운로드 속도를 포기하냐, 추출 속도를 포기하냐의 문제
                우선 영상 길이만큼 재 인코딩을 기다리는건 아닌 거 같아 mp4로 받고 m4a 를 추출하는걸로 결정
                그러니 아래 두 변수 수정 금지!
            """
            self.__video_ext = "mp4"
            self.__audio_ext = "m4a"

            # 비디오 파일 완전 경로
            self.__video_full_path = os.path.join(
                self.__download_folder,
                self.__title,
                f"{self.__title}.{self.__video_ext}",
            )

            # 음성 파일 완전 경로
            self.__audio_full_path = os.path.join(
                self.__download_folder,
                self.__title,
                f"{self.__title}.{self.__audio_ext}",
            )

            # 출력 경로에 title 얹기
            self.__output_folder = os.path.join(self.__output_folder, self.__title)
            self.__thumbnail_folder = os.path.join(
                self.__thumbnail_folder, self.__title
            )

            # 폴더 생성
            os.makedirs(self.__thumbnail_folder, exist_ok=True)
            os.makedirs(self.__output_folder, exist_ok=True)
            os.makedirs(self.__download_folder, exist_ok=True)

        except Exception as e:
            # 예외 발생시 호출한 쪽으로 떠넘긴다.
            raise e

    # public--------------------------------------------------------------

    # 다른 쓰레드에서 실행될 함수
    def extract_thumbnail_thread(self, qthread, result: list) -> None:
        print("썸네일 추출 쓰레드 시작")
        # result 에 결과를 받을 리스트를 넘긴다.
        # 파이썬에서 리스트를 인자로 넘기면 참조로 넘어가서 함수 내부에서 리스트를 수정하면
        # 함수 외부에서도 리스트가 수정된다.
        # 마치 C언어의 call by ref 같은 개념

        # 병렬 처리에 필요한 데이터 생성
        parallel_data: list[tuple[int, RangedChapter]] = []
        for i, chapter in enumerate(self.__chapters):
            parallel_data.append((i, chapter))

        max_workers = multiprocessing.cpu_count() * 2

        pool = concurrent.futures.ThreadPoolExecutor(max_workers)
        futures = [
            pool.submit(self.thumbnail_extractor, args) for args in parallel_data
        ]
        wait(futures, return_when=ALL_COMPLETED)

        for future in futures:
            result.append(future.result())

        qthread.resume()

    # 다른 쓰레드에서 실행될 함수 (챕터 별로 자르기)
    def cut_audio_thread(self, qthread, result: list):
        # 병렬 처리에 필요한 데이터 생성
        parallel_data: list[RangedChapter] = self.__chapters

        max_workers = multiprocessing.cpu_count() * 2

        pool = concurrent.futures.ThreadPoolExecutor(max_workers)
        futures = [pool.submit(self.cut_audio, args) for args in parallel_data]
        wait(futures, return_when=ALL_COMPLETED)

        for future in futures:
            result.append(future.result())

        qthread.resume()

    def get_youtube_info(self, url: str):
        # yt-dlp로 영상 정보 가져오기
        ydl = YoutubeDL({"quiet": True})
        info = ydl.extract_info(url, download=False)
        ydl.close()  # with 을 쓰지 않아서 직접 close 해줘야함
        if not info:
            raise FailtoGetInfo
        return info

    def download_video_high_quality(self, call_back) -> None:
        # yt-dlp --limit-rate 3000K -N 10 --fragment-retries 1000 --retry-sleep fragment:linear=1::2 --force-overwrites "https://www.youtube.com/watch?v=UnPyGbP0WhE&t=403s"
        with yt_dlp.YoutubeDL(
            {
                # 최고 품질 영상 mp4 & 최고 음질 m4a 로 받으나, 영상의 경우 FHD 이하로 제한한다.
                "format": f"bestvideo[height<=1080][ext={self.__video_ext}]+bestaudio[ext=m4a]/best[ext={self.__video_ext}]/best",
                "merge_output_format": self.__video_ext,
                # "outtmpl": {"default": "%(title)s.%(ext)s"},  # 제목.확장자 형식으로 저장
                "outtmpl": {"default": self.__video_full_path},
                "throttledratelimit": 102400,
                "fragment_retries": 1000,
                # "overwrites": True,
                "concurrent_fragment_downloads": 3,  # 동시에 N개의 영상 조각을 다운로드
                "retry_sleep_functions": {"fragment": lambda n: n + 1},
                "progress_hooks": [call_back],  # 다운로드 진행 상황을 알려주는 콜백 함수
            }
        ) as ydl:
            ydl.download([self.__url])

    # 음원 추출
    def extract_audio(self):
        output = self.run_ffmpeg(
            [
                "-y",
                "-i",
                self.__video_full_path,
                "-vn",
                "-acodec",
                "copy",
                self.__audio_full_path,
            ]
        )
        return output

    # 썸네일 적용
    def apply_thumbnail(self):
        # 썸네일 폴더의 모든 파일을 가져온다.
        thumbnail_files = []
        for file in os.listdir(self.__thumbnail_folder):
            thumbnail_files.append(os.path.join(self.__thumbnail_folder, file))

        # 썸네일 파일을 정렬한다.
        thumbnail_files = natsorted(thumbnail_files)

        for i, chapter in enumerate(self.chapters):
            m4a_path = os.path.join(
                self.__output_folder, chapter.title + f".{self.__audio_ext}"
            )
            self.add_album_art(m4a_path, thumbnail_files[i])

        # 작업 완료 후 다운로드 받은 영상, 추출한 음원, 썸네일 폴더를 삭제한다.
        # os.remove(f"{title}.{ext}")
        # os.remove(f"{title}.m4a")
        # shutil.rmtree(thumbnail_folder)

    # --------------------------------------------------------------------

    # --------------------------------------------------------------------

    # property------------------------------------------------------------

    @property
    def title(self) -> str:
        return self.__title

    @property
    def duration(self) -> str:
        return self.__duration

    @property
    def is_already_chapter(self) -> bool:
        return self.__is_already_chapter

    @property
    def chapters(self):
        return self.__chapters

    # --------------------------------------------------------------------

    # 챕터를 입력받고 파싱
    def parse_chapter_by_user(self, user_input: str):
        base_chapter: list[BaseChapter] = self.make_base_chapter(user_input)

        # self.update_label.emit("챕터 변환을 수행합니다.")
        ranged_chapter: list[RangedChapter] = self.convert_base_to_ranged_chapter(
            base_chapter
        )

        # Setter
        self.__chapters = ranged_chapter
        # return ranged_chapter

    # yt-dlp에서 가져온 챕터 내역을 프로그램에 알맞게 변환
    def parse_chapter_by_yt_dlp(self) -> None:
        ranged_chapter = []
        for chapter in self.__chapters:
            ranged_chapter.append(
                RangedChapter(
                    # filename_remover 작업
                    title=self.__filename_remover(chapter["title"]),
                    start_time=chapter["start_time"],
                    end_time=chapter["end_time"],
                )
            )

        # Setter
        self.__chapters = ranged_chapter
        # return ranged_chapter

    # ffmpeg로 챕터 시작 시간의 썸네일 추출
    def thumbnail_extractor(self, data: tuple[int, RangedChapter]):
        i, chapter = data
        copy_offset = self.__total_offset
        # custom offset이 적용된 경우 해당 순번의 썸네일에만 오프셋을 따로 줌 (total_offset과 합산됨)
        if i + 1 in self.__custom_offset:
            copy_offset = self.__total_offset + self.__custom_offset[i + 1]
        # 썸네일 추출
        time = str(int(chapter.start_time) + copy_offset)
        output = self.run_ffmpeg(
            [
                # -y 옵션 : 덮어쓰기
                "-y",
                "-ss",
                time,
                "-i",
                self.__video_full_path,
                "-vframes",
                "1",
                os.path.join(self.__thumbnail_folder, f"{i}.png"),
            ]
        )
        return self.__title, output

    # 챕터 별로 음원 자르기
    def cut_audio(self, chapters: RangedChapter) -> tuple[str, str]:
        # 챕터별 음원 추출
        output = self.run_ffmpeg(
            [
                "-y",
                "-i",
                self.__audio_full_path,
                "-ss",
                str(int(chapters.start_time)),
                "-to",
                str(int(chapters.end_time)),
                "-c",
                "copy",
                os.path.join(self.__output_folder, f"{chapters.title}.m4a"),
            ]
        )
        return (chapters.title, output)

    # 프로세스 실행하고 결과를 반환하는 함수
    def run_process(self, command: list[str]) -> str:
        # command ex) ['ls', '-al']

        # 명령어 실행 후, 결과를 output에 저장
        # text = True : output을 text로 저장,
        # encoding은 기본이 cp949라 문제 없이 저장할려면 utf-8로 설정
        try:
            output: str = subprocess.check_output(
                command, stderr=subprocess.STDOUT, encoding="utf-8", text=True
            )
        except:
            raise Exception("명령어 실행에 실패했습니다", command)

        return output

    # ffmpeg 실행하고 결과를 반환하는 함수 (일종의 run_process의 wrapper 함수)

    def run_ffmpeg(self, command: list[str]) -> str:
        output = self.run_process(["ffmpeg", *command])
        return output

    def run_mp4art(self, command: list[str]) -> str:
        # mp4는 인코딩 문제로 인해 utf-8을 적용하지 않는다.
        output: str = self.run_process(["mp4art", *command])
        return output

    # 1:30:00, 30:00, 30 와 같은 시간 형식 문자열을 초로 변환
    # formatted_time : 변환할 시간 형식 ex) 1:30:00, 30:00, 30
    # return : 초 단위로 변환된 시간 ex) 5400.0, 1800.0, 30.0
    # 1:30:00 => 5400.0
    # 30:00 => 1800.0
    # 30 => 30.0
    def __convert_to_seconds(self, formatted_time: str) -> float:
        # 시간 형식에 따라 적절한 포맷을 선택
        formats = ["%H:%M:%S", "%M:%S", "%S"]

        for fmt in formats:
            try:
                # 주어진 형식으로 시간을 파싱
                time_obj = datetime.strptime(formatted_time, fmt)

                # timedelta를 사용하여 초로 변환
                seconds = timedelta(
                    hours=time_obj.hour,
                    minutes=time_obj.minute,
                    seconds=time_obj.second,
                ).total_seconds()
                return seconds
            except ValueError:
                pass

        # 올바른 형식이 없는 경우 예외 처리
        raise ValueError("올바른 시간 형식이 아닙니다.")

    # 유저가 입력한 문자열 챕터 형식을 파싱해 BaseChapter 객체로 반환

    def make_base_chapter(self, user_input: str) -> list[BaseChapter]:
        pattern_lst = [
            # 01. Durarara!! OP2 │ 0:00
            r"(.+?)[ ]+(?:│|[|])*[ ]*(\d+:\d+:\d+|\d+:\d+)",
            r"(\d+:\d+:\d+|\d+:\d+)[ ]+(?:│|[|])*[ ]*(.+)",  # 00:00 유우리 - 여름소리
        ]
        success_chapter = False  # 챕터를 정상적으로 파싱했는지 여부
        raw_parsed_chapter = []

        pattern_idx = 0
        for i, pattern in enumerate(pattern_lst):
            pattern_idx = i
            raw_parsed_chapter: list[tuple[str, str]] = re.findall(pattern, user_input)

            if raw_parsed_chapter:
                success_chapter = True
                break

        if not success_chapter:
            raise Exception("챕터 파싱에 실패했습니다. 챕터 형식을 확인해주세요.")

        parsed_chapter: list[BaseChapter] = []
        # 첫번째 패턴 : 숫자가 뒤에 오는 경우

        if pattern_idx == 0:
            parsed_chapter = [
                BaseChapter(self.__filename_remover(title), time)
                for title, time in raw_parsed_chapter
            ]
        # 두번째 패턴 : 숫자가 앞에 오는 경우
        elif pattern_idx == 1:
            parsed_chapter = [
                BaseChapter(self.__filename_remover(title), time)
                for time, title in raw_parsed_chapter
            ]

        return parsed_chapter

    # 베이스 챕터들을 레인지 챕터로 변환해주는 함수.
    # BaseChapter 리스트 객체를 RangedChapter 리스트 객체로 변환한다.
    # 이 함수는 BaseChapter 리스트와 영상의 길이를 인자로 받는다.
    # 영상의 길이 ex) 1:30:00, 30:00, 30

    def convert_base_to_ranged_chapter(
        self, base_chapter: list[BaseChapter]
    ) -> list[RangedChapter]:
        ranged_chapter: list[RangedChapter] = []
        for i, element in enumerate(base_chapter):
            # 마지막 챕터인 경우 끝은 영상 끝까지
            if i == len(base_chapter) - 1:
                ranged_chapter.append(
                    RangedChapter(
                        title=element.title,
                        start_time=self.__convert_to_seconds(element.timeline),
                        end_time=self.__convert_to_seconds(self.__duration),
                    )
                )
                break
            ranged_chapter.append(
                RangedChapter(
                    title=element.title,
                    start_time=self.__convert_to_seconds(element.timeline),
                    end_time=self.__convert_to_seconds(
                        base_chapter[i + 1].timeline
                    ),  # 다음 챕터의 시작 시간
                )
            )
        return ranged_chapter

    # 경로 금지 문자 제거, HTML문자 제거

    def __filename_remover(self, string: str, remove=False) -> str:
        # 1. 폴더에 들어갈 수 없는 특수문자를 들어갈 수 있는
        # 특수한 유니코드 문자 (겉보기에 똑같은 문자)로 치환 시킨다.
        table = str.maketrans('\\/:*?"<>|.', "￦／：＊？＂˂˃｜．")

        # remove 모드가 활성화 되면 경로 금지 문자를 공백으로 치환한다.
        if remove:
            table = str.maketrans('\\/:*?"<>|.', "          ")
        processed_string: str = string.translate(table)

        # 2. \t 과 \n제거 (\t -> 공백 , \n -> 공백)
        table = str.maketrans("\t\n", "  ")
        processed_string = processed_string.translate(table)
        return processed_string

    def add_album_art(self, m4a_file_path: str, album_art_path: str) -> None:
        try:
            audio = MP4(m4a_file_path)
            audio["covr"] = [
                mutagen.mp4.MP4Cover(
                    open(album_art_path, "rb").read(),
                    imageformat=mutagen.mp4.MP4Cover.FORMAT_JPEG,
                )
            ]
            audio.save()
        except Exception as e:
            raise Exception(f"앨범 아트 추가 중 오류 발생: {e}")
