import multiprocessing
from typing import Final, Optional
from module.ui_compiler import compile_ui_to_py
import sys
from PySide6.QtCore import *
from PySide6.QtWidgets import *
import os
import glob
from pprint import pprint
import sys
import yt_dlp
from module.config import Config
from module.module import (
    add_album_art,
    convert_base_to_ranged_chapter,
    filename_remover,
    get_youtube_info,
    make_base_chapter,
    run_ffmpeg,
)
from natsort import natsorted
from type.type import RangedChapter
import concurrent.futures

# UI -> PY 컴파일
# fmt: off
ui_path = "./ui"
compiled_ui_path = "./compiled_ui"
ui_files = ['select.ui', 'input.ui', 'auto.ui']

for ui_file in ui_files:
    input_path = os.path.join(ui_path, ui_file)
    output_path = os.path.join(compiled_ui_path, f'{os.path.splitext(ui_file)[0]}.py')
    compile_ui_to_py(input_path, output_path)

from compiled_ui.select import Ui_SelectWindow
from compiled_ui.input import Ui_InputWindow
from compiled_ui.auto import Ui_AutoWindow
# fmt: on

# 전역 변수
TITLE: Final[str] = "Youtube Chapter Converter"


# 설정 파일 객체는 싱글톤으로 전역으로 사용한다.
config = Config("./settings.json")


class AutoWindow(QMainWindow, Ui_AutoWindow):
    def __init__(self) -> None:
        # 기본 설정 코드
        super().__init__()
        self.setupUi(self)

        # 제목 설정
        self.setWindowTitle(TITLE)

    def edit_log(self, log: str) -> None:
        self.textedit_log.setText(log)


class MainWindow(QMainWindow, Ui_SelectWindow):
    def __init__(self) -> None:
        # 기본 설정 코드
        super().__init__()
        self.setupUi(self)

        # 제목 설정
        self.setWindowTitle(TITLE)

        # InputWindow 창 객체
        self.input_window: Optional[InputWindow] = None

    # 자동 변환
    def auto_convert(self) -> None:
        # InputWindow 창 열기
        # 효율성을 위해 창이 열려있으면 새로 열지 않고 기존 창을 활성화한다.
        if not self.input_window or not self.input_window.isVisible():
            self.input_window = InputWindow()
            self.input_window.show()
        else:
            self.input_window.activateWindow()
        pass

    # 매뉴얼 변환
    def manual_convert(self) -> None:
        pass

    # 영상 다운로드
    def download_video(self) -> None:
        pass

    # 썸네일 적용
    def apply_thumbnail(self) -> None:
        pass

    # 해당 메인창이 꺼지면 모든 창을 종료한다.
    def closeEvent(self, event) -> None:
        # InputWindow 창이 열려있으면 닫는다.
        if self.input_window:
            self.input_window.close()

        # 본인도 종료한다.
        event.accept()


# PySide6 쓰레드 패턴 코드 참고
# https://jooji815.tistory.com/799

# 주로 봐야할 부분은 Signal 선언하고 emit하는 부분과 connect로 연결하는 부분이다.
# PySide6은 Signal, PyQT5는 pyqtSignal로 선언


class InputWindow(QMainWindow, Ui_InputWindow):
    def __init__(self) -> None:
        # 기본 설정 코드
        super().__init__()
        self.setupUi(self)

        # 제목 설정
        self.setWindowTitle(TITLE)

        # 챕터 입력 상황 체크 변수
        self.need_chapter_input = False

        # 이미 챕터가 존재하는 경우 사용할 것인지 체크하는 변수
        self.use_already_chapter = None

        # 쓰레드 변수
        self.worker: Optional[DownloadWorker] = None

        # 로그 창 변수
        self.log_window: Optional[AutoWindow] = None

        # Youtube URL 텍스트 창에서 엔터 입력시 OK 버튼 누르는 이벤트
        self.line_edit_youtube_url.returnPressed.connect(self.enter_pressed)

        self.progress_bar.hide()

    def enter_pressed(self) -> None:
        # 버튼이 활성화 되어 있는 경우에만 엔터로 버튼 클릭을 허용
        if self.btn_ok.isEnabled():
            self.download()

    # OK 버튼
    def download(self) -> None:
        # 챕터 입력을 해야 하는 상황인 경우
        if self.need_chapter_input:
            # 유저가 입력한 챕터가 비어있지 않았는지 확인하고 다시 Worker 쓰레드를 깨운다. (전역 변수를 활용해서)
            user_input = self.textedit_user_input.toPlainText()
            if not user_input.strip():
                QMessageBox.information(self, "알림", "챕터를 입력해주세요.")
                return
            else:
                # 입력 다 받았으니 쓰레드 깨우기
                self.worker.resume()
                # C-OK 버튼 비활성화
                self.btn_ok.setEnabled(False)
            return

        # 유저가 입력한 URL
        url = self.line_edit_youtube_url.text()

        if not url.strip():
            # 메세지 박스 출력
            QMessageBox.information(self, "알림", "URL을 입력해주세요.")
            return

        # OK 버튼을 누르면 쓰레드를 생성하여 작업을 수행
        # 쓰레드가 작업을 수행하는 동안은 OK 버튼을 비활성화 한다.
        self.btn_ok.setEnabled(False)
        self.worker = DownloadWorker(self)

        # 쓰레드 시그널과 슬롯 연결
        self.worker.update_label.connect(self.update_label)
        self.worker.chapter_enabled.connect(self.chapter_enabled)
        self.worker.failed_download.connect(self.failed_download)
        self.worker.already_exist_chapter.connect(self.already_exist_chapter)
        self.worker.finished.connect(self.thread_finished_job)
        self.worker.update_input_box.connect(self.update_input_box)
        self.worker.update_progress_bar.connect(self.update_progress_bar)
        self.worker.update_log.connect(self.update_log)

        # 쓰레드 작업 시작
        self.worker.start()

        # print("작업 종료")

    # 해당 창을 종료하면 쓰레드 종료 & 전부 원상 복귀 시킨다.
    def closeEvent(self, event) -> None:
        # 쓰레드 변수가 존재하면 쓰레드를 종료한다.
        if self.worker:
            self.worker.terminate()

        # 원상 복귀
        self.backup_origin()
        event.accept()

    # 원상 복귀 함수
    def backup_origin(self) -> None:
        self.need_chapter_input = False
        self.use_already_chapter = None

    # Worker Thread 의 챕터 입력 명령 함수
    @Slot()
    def chapter_enabled(self) -> None:
        self.btn_ok.setEnabled(True)
        self.btn_ok.setText("C-OK")
        # 챕터 입력 상황이 됨 = True
        self.need_chapter_input = True

    @Slot(str)
    def update_label(self, log: str) -> None:
        self.label_status.setText(f"Status : {log}")

    # 다운로드 실패시
    @Slot()
    def failed_download(self) -> None:
        self.btn_ok.setEnabled(True)
        self.backup_origin()

    # 영상에 이미 챕터가 존재하는 경우
    @Slot()
    def already_exist_chapter(self) -> None:
        self.use_already_chapter = QMessageBox.question(
            self,
            "알림",
            "영상에 이미 챕터가 존재합니다 영상의 챕터를 사용하시겠습니까 ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        # 입력 받고 나서 쓰레드를 깨운다.
        self.worker.resume()

    # 쓰레드 작업 종료시
    @Slot()
    def thread_finished_job(self) -> None:
        self.btn_ok.setEnabled(True)
        self.btn_ok.setText("OK")
        self.progress_bar.hide()
        self.backup_origin()
        if self.log_window:
            self.log_window.hide()

    # 챕터 입력 박스 업데이트
    @Slot(str)
    def update_input_box(self, chapters: str) -> None:
        self.textedit_user_input.append(chapters)

    # 프로그레스 바 업데이트
    @Slot(int)
    def update_progress_bar(self, value: int) -> None:
        if not self.progress_bar.isVisible():
            self.progress_bar.show()
        self.progress_bar.setValue(value)
        if value == 100:
            self.progress_bar.hide()

    # 로그 업데이트 - INPUT Window에서 Log Window를 컨트롤한다.
    # UI 업데이트 관련 로직은 전부 메인 쓰레드에서 처리하도록 한다.
    @Slot(str)
    def update_log(self, log: str) -> None:
        if not self.log_window or not self.log_window.isVisible():
            self.log_window = AutoWindow()
            self.log_window.show()
        else:
            self.log_window.activateWindow()
        self.log_window.textedit_log.append(log)


class DownloadWorker(QThread):
    # Custom Signal 생성
    update_label = Signal(str)  # 오른쪽 아래 Status Label 업데이트
    update_log = Signal(str)  # 로그 창 업데이트 (로그 창 안열려 있으면 자동으로 열리고 로그 출력됨)
    update_input_box = Signal(str)  # 챕터 입력 박스 업데이트
    chapter_enabled = Signal()  # 챕터 입력 상황이 됨
    failed_download = Signal()  # 다운로드 실패시
    already_exist_chapter = Signal()  # 영상에 이미 챕터가 존재하는 경우 유저 입력 메세지 박스 요청
    update_progress_bar = Signal(int)  # 프로그레스 바 업데이트

    def __init__(self, parent: InputWindow) -> None:
        # 부모 생성자 호출
        super().__init__()

        # 유저가 입력한 윈도우 Class 객체 (Read Only)
        self.input_window = parent

        # 쓰레드 잠들기 여부
        self.is_sleep = False

    # 쓰레드 잠드는 함수 (이 함수 사용시 외부 쓰레드에서 깨워야함.)
    def pause(self) -> None:
        self.is_sleep = True
        while self.is_sleep:
            pass

    # 쓰레드 깨우는 함수 (외부 쓰레드에서 깨울 시 이 함수 호출)
    def resume(self) -> None:
        self.is_sleep = False

    # 유저로부터 챕터를 입력받고 파싱
    def parse_chapter_by_user(self, duration) -> list[RangedChapter]:
        self.update_label.emit("챕터를 위 박스에 입력해주세요. 다 입력했으면 C-OK 버튼을 누릅니다.")
        self.chapter_enabled.emit()  # 챕터 박스 입력 명령을 메인 윈도우에 전달

        # 챕터를 입력할 때까지 Worker 쓰레드는 대기 (메인 쓰레드의 동작 대기)
        # while not is_chapter_input_finish:
        #     pass
        self.pause()

        # 챕터 입력이 완료되면 작업 시작
        self.update_label.emit("챕터 생성 진행 중...")

        input_chapters: str = self.input_window.textedit_user_input.toPlainText()
        base_chapter = make_base_chapter(input_chapters)

        pprint(base_chapter)

        self.update_label.emit("챕터 변환을 수행합니다.")
        ranged_chapter = convert_base_to_ranged_chapter(base_chapter, duration)
        return ranged_chapter

    # yt-dlp에서 가져온 챕터 내역을 프로그램에 알맞게 변환
    def parse_chapter_by_yt_dlp(self, chapters: dict) -> list[RangedChapter]:
        ranged_chapter = []
        for chapter in chapters:
            ranged_chapter.append(
                RangedChapter(
                    # filename_remover 작업
                    title=filename_remover(chapter["title"]),
                    start_time=chapter["start_time"],
                    end_time=chapter["end_time"],
                )
            )
        return ranged_chapter

    def my_hook(self, d) -> None:
        if d["status"] == "finished":
            self.update_label.emit("다운로드가 완료되었습니다. 병합 진행중...")
        if d["status"] == "downloading":
            # d 데이터 파일로 쓰고 프로그램 종료
            # with open("data.json", "w", encoding="utf-8") as f:
            #     json.dump(d, f)
            # sys.exit()

            # self.update_progress_bar.emit(d["_percent_str"])
            # self.update_log.emit(d["_percent_str"])

            total_bytes = ""
            if "total_bytes" in d:
                total_bytes = "total_bytes"
            elif "total_bytes_estimate" in d:
                total_bytes = "total_bytes_estimate"
            else:
                return

            percentage = round(
                float(d["downloaded_bytes"]) / float(d[total_bytes]) * 100, 1
            )
            self.update_progress_bar.emit(percentage)

    # ffmpeg로 챕터 시작 시간의 썸네일 추출
    def thumbnail_extractor(self, data: tuple[int, RangedChapter]):
        i, chapter = data
        copy_offset = self.total_offset
        # custom offset이 적용된 경우 해당 순번의 썸네일에만 오프셋을 따로 줌 (total_offset과 합산됨)
        if i + 1 in self.custom_offset:
            copy_offset = self.total_offset + self.custom_offset[i + 1]
        # 썸네일 추출
        time = str(int(chapter.start_time) + copy_offset)
        output = run_ffmpeg(
            [
                # -y 옵션 : 덮어쓰기
                "-y",
                "-ss",
                time,
                "-i",
                self.video_full_path,
                "-vframes",
                "1",
                os.path.join(self.thumbnail_folder, f"{i}.png"),
            ]
        )
        return self.title, output

    # 챕터 별로 음원 자르기
    def cut_audio(self, chapters: RangedChapter) -> tuple[str, str]:
        # 챕터별 음원 추출
        output = run_ffmpeg(
            [
                "-y",
                "-i",
                self.audio_full_path,
                "-ss",
                str(int(chapters.start_time)),
                "-to",
                str(int(chapters.end_time)),
                "-c",
                "copy",
                os.path.join(self.output_folder, f"{chapters.title}.m4a"),
            ]
        )
        return (chapters.title, output)

    def run(self) -> None:
        try:
            self.update_label.emit("유튜브 영상 정보를 가져오는 중...")

            # InputWindow 에서 넘겨 받은 본인(self) 변수를 이용해 UI 요소들에 접근한다.
            # 참고로 이 방식으론 접근해서 읽기만 해야지 쓰기는 하면 안된다.
            # 쓰고 싶으면 Signal & Slot 을 이용해 Thread Safe 하게 접근해야 한다.

            # 생성자 대신에 run 함수 내부에서 멤버 변수들을 초기화 한다.
            self.url = self.input_window.line_edit_youtube_url.text()
            self.info = get_youtube_info(self.url)

            # filename_remover 작업
            self.title: str = filename_remover(self.info["title"])
            self.duration: str = self.info["duration_string"]
            self.chapters = self.info["chapters"]

            # 설정 파일에서 설정값을 가져옴
            self.thumbnail_folder = config.get().thumbnail_folder
            self.output_folder = config.get().output_folder
            self.custom_offset = config.get().custom_offset
            self.total_offset = config.get().total_offset
            self.download_folder = config.get().download_folder

            self.ext = "mp4"  # 수정 금지!

            # 비디오 파일 완전 경로
            self.video_full_path = os.path.join(
                self.download_folder, f"{self.title}.{self.ext}"
            )

            # 음성 파일 완전 경로
            self.audio_full_path = os.path.join(
                self.download_folder, f"{self.title}.m4a"
            )

            self.update_label.emit(f"{self.title} | {self.duration}")

            if self.chapters != None:
                # 영상에 이미 챕터가 존재하는 경우 RangedChapter 에 맞게 변환한다.
                # 메인 쓰레드에게 메세지 입력을 요청하기 위해 시그널을 보내고 대기한다.
                self.already_exist_chapter.emit()

                # 메인 쓰레드가 사용자의 선택을 기다리는 동안 Worker 쓰레드는 대기한다.
                # 입력이 끝나면 메인 쓰레드에서 알아서 깨워준다.
                self.pause()

                if (
                    self.input_window.use_already_chapter
                    == QMessageBox.StandardButton.Yes
                ):
                    self.chapters = self.parse_chapter_by_yt_dlp(self.chapters)
                else:
                    self.chapters = self.parse_chapter_by_user(self.duration)
            else:
                self.chapters = self.parse_chapter_by_user(self.duration)

            # 여기까지 오면 chapters는 확정된 상태 = Not Empty
            pprint(self.chapters)

            # 최고 화질 + 최고 음질로 영상 다운로드
            # 참고 : https://github.com/yt-dlp/yt-dlp/issues/3398
            # mp4 영상은 최고 용량이 webm 용량 대비 너무 커서 webm을 택했으나
            # mp4는 음원 분리가 바로 되나 webm은 재 인코딩 과정이 필요해 매우 오래 걸림.
            # 따라서 어쩔 수 없이 mp4를 택함.

            self.update_label.emit("최고 품질로 영상을 다운로드 합니다.")

            # yt-dlp --limit-rate 3000K -N 10 --fragment-retries 1000 --retry-sleep fragment:linear=1::2 --force-overwrites "https://www.youtube.com/watch?v=UnPyGbP0WhE&t=403s"

            with yt_dlp.YoutubeDL(
                {
                    # 최고 품질 영상 mp4 & 최고 음질 m4a 로 받으나, 영상의 경우 FHD 이하로 제한한다.
                    "format": f"bestvideo[height<=1080][ext={self.ext}]+bestaudio[ext=m4a]/best[ext={self.ext}]/best",
                    "merge_output_format": self.ext,
                    # "outtmpl": {"default": "%(title)s.%(ext)s"},  # 제목.확장자 형식으로 저장
                    "outtmpl": {"default": self.video_full_path},
                    "throttledratelimit": 102400,
                    "fragment_retries": 1000,
                    # "overwrites": True,
                    "concurrent_fragment_downloads": 3,  # 동시에 N개의 영상 조각을 다운로드
                    "retry_sleep_functions": {"fragment": lambda n: n + 1},
                    "progress_hooks": [self.my_hook],
                }
            ) as ydl:
                ydl.download([self.url])
            self.update_label.emit("다운로드가 완료되었습니다.")

            # 각 챕터 시작 시간의 썸네일을 ffmpeg를 이용해 추출한다.
            self.update_label.emit("썸네일을 추출합니다.")

            # 썸네일 저장용 폴더 생성
            os.makedirs(self.thumbnail_folder, exist_ok=True)

            # 병렬 처리에 필요한 데이터 생성
            parallel_data: list[tuple[int, RangedChapter]] = []
            for i, chapter in enumerate(self.chapters):
                parallel_data.append((i, chapter))

            # 동시에 실행될 최대 프로세스 수를 정의합니다.
            # 이 숫자를 조절하여 동시에 실행되는 프로세스 수를 제한할 수 있습니다.
            # 여기선 cpu 코어 수 * 2 로 설정
            max_workers = multiprocessing.cpu_count() * 2

            # multiprocessing.Pool을 사용하여 병렬 처리를 수행합니다.

            with concurrent.futures.ThreadPoolExecutor(max_workers) as executor:
                # map 메서드를 사용하여 함수를 병렬로 실행합니다.
                # your_function이 your_data_list의 각 아이템에 대해 병렬로 실행됩니다.
                results = executor.map(self.thumbnail_extractor, parallel_data)

                # 파이썬의 with은 scope를 생성하지 않는다고 함.
                # with문을 벗어나서도 with안에 있는 results 변수를 사용할 수 있나봄 -.-
                # 더불어 if, for , while 도 스코프를 생성하지 않는다고함.
                # https://stackoverflow.com/questions/45100271/scope-of-variable-within-with-statement
                # 파이썬은 지역변수 범위는 함수 안에서 결정되는듯 하다.
                # https://i-never-stop-study.tistory.com/14
                # 파이썬의 유효범위(scope)는 함수를 통해서 생성됩니다.
                # https://justmakeyourself.tistory.com/entry/python-scope
                # 지금까지 잘못 알고 있었구만;;

                # 일단 아래 코드는 스코프 문제가 아니여도 with 밖으로 빼면 안되는듯.
                # 그러면 executor가 close 되서 실시간으로 결과를 받을 수 없나봄.
                # 작업 결과를 확인합니다.
                for result in results:
                    self.update_label.emit(f"{result[0]} 썸네일 추출 완료")
                    self.update_log.emit(result[1])


            # self.update_input_box.emit(results)

            self.update_label.emit("썸네일 추출이 완료되었습니다.")

            # 다운로드 받은 영상에서 무손실 음원 m4a를 추출한다
            self.update_label.emit("음원을 추출합니다.")
            output = run_ffmpeg(
                [
                    "-y",
                    "-i",
                    self.video_full_path,
                    "-vn",
                    "-acodec",
                    "copy",
                    self.audio_full_path,
                ]
            )

            # 추출한 음원을 챕터별로 자른다.
            self.update_label.emit("음원을 챕터별로 자릅니다.")
            os.makedirs(self.output_folder, exist_ok=True)

            # 병렬 처리
            with concurrent.futures.ThreadPoolExecutor(max_workers) as executor:
                # map 메서드를 사용하여 함수를 병렬로 실행합니다.
                # your_function이 your_data_list의 각 아이템에 대해 병렬로 실행됩니다.
                results = executor.map(self.cut_audio, self.chapters)

                # 작업 결과를 확인합니다.
                for result in results:
                    self.update_label.emit(f"{result[0]}.m4a 추출 완료")
                    self.update_log.emit(result[1])
                    print(result)

            # 챕터별로 자른 음원에 썸네일을 붙인다.
            self.update_label.emit("썸네일을 적용합니다.")

            # 썸네일 폴더의 모든 파일을 가져온다.
            # thumbnail_files = os.listdir(thumbnail_folder)
            thumbnail_files = glob.glob(os.path.join(self.thumbnail_folder, "*.png"))
            thumbnail_files = natsorted(thumbnail_files)

            for i, chapter in enumerate(self.chapters):
                m4a_path = os.path.join(self.output_folder, chapter.title + ".m4a")
                add_album_art(m4a_path, thumbnail_files[i])
                self.update_label.emit(f"{chapter.title}.m4a 썸네일 적용 완료")

            # 작업 완료 후 다운로드 받은 영상, 추출한 음원, 썸네일 폴더를 삭제한다.
            # os.remove(f"{title}.{ext}")
            # os.remove(f"{title}.m4a")
            # shutil.rmtree(thumbnail_folder)

            self.update_label.emit("작업이 완료되었습니다.")

        except Exception as e:
            print(e)
            self.update_label.emit("작업중 오류가 발생했습니다.")
            self.failed_download.emit()
            return


# 메인 윈도우 실행
app = QApplication(sys.argv)
app.setStyleSheet(open("theme.css", encoding="utf-8").read())

window = MainWindow()
window.show()
sys.exit(app.exec())
