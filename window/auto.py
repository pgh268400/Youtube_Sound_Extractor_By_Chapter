from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from compiled_ui.log import Ui_LogWindow
from global_data import icon_path, title


class LogWindow(QMainWindow, Ui_LogWindow):
    def __init__(self) -> None:
        # 기본 설정 코드
        super().__init__()
        self.setupUi(self)

        # 제목 설정
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(icon_path))

    def edit_log(self, log: str) -> None:
        self.textedit_log.setText(log)
