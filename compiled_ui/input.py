# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'input.ui'
##
## Created by: Qt User Interface Compiler version 6.6.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (
    QCoreApplication,
    QDate,
    QDateTime,
    QLocale,
    QMetaObject,
    QObject,
    QPoint,
    QRect,
    QSize,
    QTime,
    QUrl,
    Qt,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QConicalGradient,
    QCursor,
    QFont,
    QFontDatabase,
    QGradient,
    QIcon,
    QImage,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
    QRadialGradient,
    QTransform,
)
from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class Ui_InputWindow(object):
    def setupUi(self, InputWindow):
        if not InputWindow.objectName():
            InputWindow.setObjectName("InputWindow")
        InputWindow.resize(502, 500)
        self.centralwidget = QWidget(InputWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName("label")

        self.horizontalLayout.addWidget(self.label)

        self.line_edit_youtube_url = QLineEdit(self.centralwidget)
        self.line_edit_youtube_url.setObjectName("line_edit_youtube_url")

        self.horizontalLayout.addWidget(self.line_edit_youtube_url)

        self.btn_ok = QPushButton(self.centralwidget)
        self.btn_ok.setObjectName("btn_ok")

        self.horizontalLayout.addWidget(self.btn_ok)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.textedit_user_input = QTextEdit(self.centralwidget)
        self.textedit_user_input.setObjectName("textedit_user_input")

        self.verticalLayout.addWidget(self.textedit_user_input)

        self.label_status = QLabel(self.centralwidget)
        self.label_status.setObjectName("label_status")
        self.label_status.setAlignment(
            Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter
        )

        self.verticalLayout.addWidget(self.label_status)

        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        InputWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(InputWindow)
        self.btn_ok.clicked.connect(InputWindow.download)
        self.line_edit_youtube_url.returnPressed.connect(InputWindow.download)

        QMetaObject.connectSlotsByName(InputWindow)

    # setupUi

    def retranslateUi(self, InputWindow):
        InputWindow.setWindowTitle(
            QCoreApplication.translate("InputWindow", "MainWindow", None)
        )
        self.label.setText(
            QCoreApplication.translate("InputWindow", "Youtube URL", None)
        )
        self.btn_ok.setText(QCoreApplication.translate("InputWindow", "OK", None))
        self.label_status.setText(
            QCoreApplication.translate("InputWindow", "Status : Null", None)
        )

    # retranslateUi
