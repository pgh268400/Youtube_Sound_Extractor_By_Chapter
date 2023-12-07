# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'select.ui'
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

class Ui_SelectWindow(object):
    def setupUi(self, SelectWindow):
        if not SelectWindow.objectName():
            SelectWindow.setObjectName(u"SelectWindow")
        SelectWindow.resize(383, 272)
        SelectWindow.setStyleSheet(u"")
        self.centralwidget = QWidget(SelectWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.btn_auto_convert = QPushButton(self.centralwidget)
        self.btn_auto_convert.setObjectName(u"btn_auto_convert")
        self.btn_auto_convert.setGeometry(QRect(20, 20, 341, 51))
        self.btn_auto_convert.setStyleSheet(u"*{\n"
"border-bottom-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(0, 0, 0, 255), stop:1 rgba(255, 255, 255, 255));\n"
"}")
        self.pushButton = QPushButton(self.centralwidget)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(20, 80, 341, 51))
        self.pushButton_2 = QPushButton(self.centralwidget)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setGeometry(QRect(20, 140, 341, 51))
        self.pushButton_3 = QPushButton(self.centralwidget)
        self.pushButton_3.setObjectName(u"pushButton_3")
        self.pushButton_3.setGeometry(QRect(20, 200, 341, 51))
        SelectWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(SelectWindow)
        self.btn_auto_convert.clicked.connect(SelectWindow.auto_convert)
        self.pushButton.clicked.connect(SelectWindow.manual_convert)
        self.pushButton_2.clicked.connect(SelectWindow.download_video)
        self.pushButton_3.clicked.connect(SelectWindow.apply_thumbnail)

        QMetaObject.connectSlotsByName(SelectWindow)
    # setupUi

    def retranslateUi(self, SelectWindow):
        SelectWindow.setWindowTitle(QCoreApplication.translate("SelectWindow", u"MainWindow", None))
        self.btn_auto_convert.setText(QCoreApplication.translate("SelectWindow", u"\uc790\ub3d9 \ubcc0\ud658", None))
        self.pushButton.setText(QCoreApplication.translate("SelectWindow", u"\uc218\ub3d9 \ubcc0\ud658", None))
        self.pushButton_2.setText(QCoreApplication.translate("SelectWindow", u"\uc601\uc0c1 \ub2e4\uc6b4\ub85c\ub4dc", None))
        self.pushButton_3.setText(QCoreApplication.translate("SelectWindow", u"\uc378\ub124\uc77c \uc801\uc6a9", None))
    # retranslateUi

