# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'log.ui'
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
from PySide6.QtWidgets import (QApplication, QMainWindow, QSizePolicy, QTextEdit,
    QWidget)

class Ui_LogWindow(object):
    def setupUi(self, LogWindow):
        if not LogWindow.objectName():
            LogWindow.setObjectName(u"LogWindow")
        LogWindow.resize(525, 408)
        self.centralwidget = QWidget(LogWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.textedit_log = QTextEdit(self.centralwidget)
        self.textedit_log.setObjectName(u"textedit_log")
        self.textedit_log.setGeometry(QRect(20, 20, 481, 361))
        self.textedit_log.setReadOnly(True)
        LogWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(LogWindow)

        QMetaObject.connectSlotsByName(LogWindow)
    # setupUi

    def retranslateUi(self, LogWindow):
        LogWindow.setWindowTitle(QCoreApplication.translate("LogWindow", u"MainWindow", None))
    # retranslateUi

