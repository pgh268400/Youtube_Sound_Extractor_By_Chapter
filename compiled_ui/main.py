# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 6.6.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QSizePolicy,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(551, 271)
        MainWindow.setStyleSheet(u"")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.btn_auto = QPushButton(self.centralwidget)
        self.btn_auto.setObjectName(u"btn_auto")
        self.btn_auto.setGeometry(QRect(20, 20, 251, 51))
        self.btn_auto.setStyleSheet(u"*{\n"
"border-bottom-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(0, 0, 0, 255), stop:1 rgba(255, 255, 255, 255));\n"
"}")
        self.btn_manual = QPushButton(self.centralwidget)
        self.btn_manual.setObjectName(u"btn_manual")
        self.btn_manual.setGeometry(QRect(20, 80, 251, 51))
        self.btn_download = QPushButton(self.centralwidget)
        self.btn_download.setObjectName(u"btn_download")
        self.btn_download.setGeometry(QRect(20, 140, 251, 51))
        self.btn_apply_thumb = QPushButton(self.centralwidget)
        self.btn_apply_thumb.setObjectName(u"btn_apply_thumb")
        self.btn_apply_thumb.setGeometry(QRect(20, 200, 251, 51))
        self.btn_open_thumb = QPushButton(self.centralwidget)
        self.btn_open_thumb.setObjectName(u"btn_open_thumb")
        self.btn_open_thumb.setGeometry(QRect(280, 140, 251, 51))
        self.btn_open_thumb.setStyleSheet(u"*{\n"
"border-bottom-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(0, 0, 0, 255), stop:1 rgba(255, 255, 255, 255));\n"
"}")
        self.btn_open_output = QPushButton(self.centralwidget)
        self.btn_open_output.setObjectName(u"btn_open_output")
        self.btn_open_output.setGeometry(QRect(280, 20, 251, 51))
        self.btn_open_output.setStyleSheet(u"*{\n"
"border-bottom-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(0, 0, 0, 255), stop:1 rgba(255, 255, 255, 255));\n"
"}")
        self.btn_open_source = QPushButton(self.centralwidget)
        self.btn_open_source.setObjectName(u"btn_open_source")
        self.btn_open_source.setGeometry(QRect(280, 80, 251, 51))
        self.btn_open_source.setStyleSheet(u"*{\n"
"border-bottom-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(0, 0, 0, 255), stop:1 rgba(255, 255, 255, 255));\n"
"}")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.btn_auto.clicked.connect(MainWindow.auto_convert)
        self.btn_manual.clicked.connect(MainWindow.manual_convert)
        self.btn_download.clicked.connect(MainWindow.download_video)
        self.btn_apply_thumb.clicked.connect(MainWindow.apply_thumbnail)
        self.btn_open_output.clicked.connect(MainWindow.open_output)
        self.btn_open_source.clicked.connect(MainWindow.open_source)
        self.btn_open_thumb.clicked.connect(MainWindow.open_thumb)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.btn_auto.setText(QCoreApplication.translate("MainWindow", u"\uc790\ub3d9 \ubcc0\ud658", None))
        self.btn_manual.setText(QCoreApplication.translate("MainWindow", u"\uc218\ub3d9 \ubcc0\ud658", None))
        self.btn_download.setText(QCoreApplication.translate("MainWindow", u"\uc601\uc0c1 \ub2e4\uc6b4\ub85c\ub4dc", None))
        self.btn_apply_thumb.setText(QCoreApplication.translate("MainWindow", u"\uc378\ub124\uc77c \uc801\uc6a9", None))
        self.btn_open_thumb.setText(QCoreApplication.translate("MainWindow", u"\uc378\ub124\uc77c \ud3f4\ub354 \uc5f4\uae30", None))
        self.btn_open_output.setText(QCoreApplication.translate("MainWindow", u"\ucd9c\ub825 \ud3f4\ub354 \uc5f4\uae30", None))
        self.btn_open_source.setText(QCoreApplication.translate("MainWindow", u"\uc601\uc0c1 + \uc74c\uc6d0 \ud3f4\ub354 \uc5f4\uae30", None))
    # retranslateUi

