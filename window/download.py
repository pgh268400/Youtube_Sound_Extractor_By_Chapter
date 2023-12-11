from compiled_ui.input import Ui_InputWindow
from global_data import icon_path, title
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *

from module.extractor import YoutubeExtractor
from module.module import escape_ansi_color_pattern


class DownloadWindow(QMainWindow, Ui_InputWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(icon_path))

        # UI요소 숨기기
        self.textedit_user_input.setVisible(False)

        # 높이, 폭 고정
        self.setFixedHeight(100)
        self.setFixedWidth(self.width())

    # 프로그레스 바 업데이트
    @Slot(int)
    def update_progress_bar(self, value: int) -> None:
        if not self.progress_bar.isVisible():
            self.progress_bar.show()
        self.progress_bar.setValue(value)
        if value == 100:
            self.progress_bar.hide()

    # 상태 라벨 업데이트
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

        # 오류 메세지 박스 출력
        QMessageBox.critical(self, "오류", err)

    def download(self) -> None:
        # 내용 비었는지 확인
        if not self.line_edit_youtube_url.text().strip():
            QMessageBox.critical(self, "Error", "내용을 입력해주세요")
            return

        # 쓰레드 실행
        self.worker = Worker(self)
        self.worker.update_progress_bar.connect(self.update_progress_bar)
        self.worker.update_label.connect(self.update_label)
        self.worker.failed_download.connect(self.failed_download)
        self.worker.start()

        # 버튼 비활성화
        self.btn_ok.setEnabled(False)

    # 종료 이벤트
    def closeEvent(self, event) -> None:
        # 쓰레드 강제 종료
        if self.worker:
            self.worker.terminate()


class Worker(QThread):
    update_progress_bar = Signal(int)
    update_label = Signal(str)
    failed_download = Signal(str)

    def __init__(self, parent: DownloadWindow) -> None:
        super().__init__()
        self.parent_window = parent

    def run(self) -> None:
        try:
            url = self.parent_window.line_edit_youtube_url.text().strip()
            self.update_label.emit("다운로드 중입니다")
            self.yt = YoutubeExtractor(url)
            self.yt.download_video_high_quality(self.progress_call_back)
        except:
            self.failed_download.emit(escape_ansi_color_pattern(str(e)))

    def progress_call_back(self, data) -> None:
        if data["status"] == "finished":
            self.update_label.emit("m4a 다운로드, 병합 진행 중...")

        if data["status"] == "downloading":
            # d 데이터 파일로 쓰고 프로그램 종료
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
