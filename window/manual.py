# PySide6 쓰레드 패턴 코드 참고
# https://jooji815.tistory.com/799

# 주로 봐야할 부분은 Signal 선언하고 emit하는 부분과 connect로 연결하는 부분이다.
# PySide6은 Signal, PyQT5는 pyqtSignal로 선언

from pprint import pprint
import threading
from typing import Optional
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from compiled_ui.input import Ui_InputWindow
from global_data import icon_path, title
from module.extractor import YoutubeExtractor
from module.module import *


from window.auto import LogWindow


class ManualWindow(QMainWindow, Ui_InputWindow):
    def __init__(self) -> None:
        # 기본 설정 코드
        super().__init__()
        self.setupUi(self)

        # 제목 설정
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(icon_path))

        # 챕터 입력 상황 체크 변수
        self.need_chapter_input = False

        # 이미 챕터가 존재하는 경우 사용할 것인지 체크하는 변수
        self.use_already_chapter = None

        # 쓰레드 변수
        self.worker: Optional[DownloadWorker] = None

        # 로그 창 변수
        self.log_window: Optional[LogWindow] = None

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
        self.update_label("챕터를 위 박스에 입력해주세요. 다 입력했으면 C-OK 버튼을 누릅니다.")
        self.btn_ok.setEnabled(True)
        self.btn_ok.setText("C-OK")
        # 챕터 입력 상황이 됨 = True
        self.need_chapter_input = True

    @Slot(str)
    def update_label(self, log: str) -> None:
        # log 글자수가 길면 자르기
        if len(log) > 50:
            log = log[:50] + "..."
        self.label_status.setText(f"Status : {log}")

    # 다운로드 실패시
    @Slot(str)
    def failed_download(self, err) -> None:
        self.btn_ok.setEnabled(True)
        self.backup_origin()

        # 오류 메세지 박스 출력
        QMessageBox.critical(self, "오류", err)

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
            self.log_window = LogWindow()
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
    failed_download = Signal(str)  # 다운로드 실패시
    already_exist_chapter = Signal()  # 영상에 이미 챕터가 존재하는 경우 유저 입력 메세지 박스 요청
    update_progress_bar = Signal(int)  # 프로그레스 바 업데이트

    def __init__(self, parent: ManualWindow) -> None:
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

    def progress_call_back(self, data) -> None:
        if data["status"] == "finished":
            self.update_label.emit("다운로드가 완료되었습니다. 병합 진행중...")

        if data["status"] == "downloading":
            # d 데이터 파일로 쓰고 프로그램 종료
            # with open("data.json", "w", encoding="utf-8") as f:
            #     json.dump(d, f)
            # sys.exit()

            # self.update_progress_bar.emit(d["_percent_str"])
            # self.update_log.emit(d["_percent_str"])

            total_bytes = ""
            if "total_bytes" in data:
                total_bytes = "total_bytes"
            elif "total_bytes_estimate" in data:
                total_bytes = "total_bytes_estimate"
            else:
                return

            percentage = round(
                float(data["downloaded_bytes"]) / float(data[total_bytes]) * 100, 1
            )
            self.update_progress_bar.emit(percentage)

    def parse_chapter(self) -> None:
        self.chapter_enabled.emit()  # 챕터 박스 입력 명령을 메인 윈도우에 전달
        self.pause()
        self.input = self.input_window.textedit_user_input.toPlainText()
        self.yt.parse_chapter_by_user(self.input)

    def run(self) -> None:
        try:
            self.update_label.emit("유튜브 영상 정보를 가져오는 중...")

            # InputWindow 에서 넘겨 받은 본인(self) 변수를 이용해 UI 요소들에 접근한다.
            # 참고로 이 방식으론 접근해서 읽기만 해야지 쓰기는 하면 안된다.
            # 쓰고 싶으면 Signal & Slot 을 이용해 Thread Safe 하게 접근해야 한다.

            self.url = self.input_window.line_edit_youtube_url.text()

            # 객체 생성, 해당 객체를 활용하여 기능 수행
            self.yt = YoutubeExtractor(self.url)

            self.update_label.emit(f"{self.yt.title} | {self.yt.duration}")

            if self.yt.is_already_chapter:
                # 영상에 이미 챕터가 존재하는 경우 RangedChapter 에 맞게 변환한다.
                # 메인 쓰레드에게 메세지 입력을 요청하기 위해 시그널을 보내고 대기한다.
                self.already_exist_chapter.emit()

                # 메인 쓰레드가 사용자의 선택을 기다리는 동안 Worker 쓰레드는 대기한다.
                # 입력이 끝나면 메인 쓰레드에서 알아서 깨워준다.
                self.pause()

                # 객체에 내부 Chapter 멤버 변수가 변하도록 변환 요청 (Setter 호출)
                if (
                    self.input_window.use_already_chapter
                    == QMessageBox.StandardButton.Yes
                ):
                    self.yt.parse_chapter_by_yt_dlp()
                else:
                    self.parse_chapter()
            else:
                self.parse_chapter()

            # 여기까지 오면 chapters는 확정된 상태 = Not Empty
            pprint(self.yt.chapters)

            self.update_label.emit("최고 품질로 영상을 다운로드 합니다.")
            self.yt.download_video_high_quality(call_back=self.progress_call_back)

            self.update_label.emit("다운로드가 완료되었습니다.")

            # 각 챕터 시작 시간의 썸네일을 ffmpeg를 이용해 추출한다.
            self.update_label.emit("썸네일을 추출합니다.")

            # 쓰레드를 호출하여 작업 실행, QTHREAD 내부에서 바로 ThreadPoolExecutor를 돌리니깐 코드가 멈춰버림.
            # 따라서 QThread 안에서 쓰레드를 하나 더 만들어서 작업을 수행하도록 함.
            results = []
            t = threading.Thread(
                target=self.yt.extract_thumbnail_thread, args=(self, results)
            )
            t.start()
            self.pause()

            for result in results:
                self.update_label.emit(f"{result[0]} 썸네일 추출 완료")
                self.update_log.emit(result[1])

            self.update_label.emit("썸네일 추출이 완료되었습니다.")

            # 다운로드 받은 영상에서 무손실 음원 m4a를 추출한다
            self.update_label.emit("음원을 추출합니다.")
            self.yt.extract_audio()

            # 추출한 음원을 챕터별로 자른다.
            self.update_label.emit("음원을 챕터별로 자릅니다.")

            # 쓰레드 실행
            results = []
            t = threading.Thread(target=self.yt.cut_audio_thread, args=(self, results))
            t.start()
            self.pause()

            # 작업 결과를 확인합니다.
            for result in results:
                self.update_label.emit(f"{result[0]}.m4a 추출 중")
                self.update_log.emit(result[1])
                print(result)

            # 챕터별로 자른 음원에 썸네일을 붙인다.
            self.update_label.emit("썸네일을 적용합니다.")
            self.yt.apply_thumbnail()
            self.update_label.emit(f"{self.yt.title}.m4a 썸네일 적용 완료")

            self.update_label.emit("작업이 완료되었습니다.")

        except Exception as e:
            print(e)
            self.update_label.emit("작업중 오류가 발생했습니다.")
            self.failed_download.emit(escape_ansi_color_pattern(str(e)))
            return
