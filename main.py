from typing import Optional
from global_data import icon_path, theme_path, title
from module.ui_compiler import compile_ui_to_py_multi
import sys
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *
import sys

# UI -> PY 컴파일-------------------------------------
# fmt: off
ui_path = "./ui"
compiled_ui_path = "./compiled_ui"
ui_files = ['select.ui', 'input.ui', 'auto.ui']
compile_ui_to_py_multi(ui_path, compiled_ui_path, ui_files)

# 컴파일을 먼저 하고 UI를 import 한다.
from compiled_ui.select import Ui_SelectWindow
from window.input import InputWindow
# fmt: on
# -----------------------------------------------------


class MainWindow(QMainWindow, Ui_SelectWindow):
    def __init__(self) -> None:
        # 기본 설정 코드
        super().__init__()
        self.setupUi(self)

        # 제목 설정
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(icon_path))

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

        # 쓰레드도 강제 종료한다.
        if self.input_window.worker:
            self.input_window.worker.terminate()

        # 본인도 종료한다.
        event.accept()


# 메인 윈도우 실행
app = QApplication(sys.argv)

import qtmodern.styles
import qtmodern.windows

qtmodern.styles.light(app)

app.setStyleSheet(open(theme_path, encoding="utf-8").read())

window = MainWindow()
window.show()
sys.exit(app.exec())
