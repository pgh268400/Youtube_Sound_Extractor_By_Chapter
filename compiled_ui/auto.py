# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'auto.ui'
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

class Ui_AutoWindow(object):
    def setupUi(self, AutoWindow):
        if not AutoWindow.objectName():
            AutoWindow.setObjectName(u"AutoWindow")
        AutoWindow.resize(525, 408)
        self.centralwidget = QWidget(AutoWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.textedit_log = QTextEdit(self.centralwidget)
        self.textedit_log.setObjectName(u"textedit_log")
        self.textedit_log.setGeometry(QRect(20, 20, 481, 361))
        AutoWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(AutoWindow)

        QMetaObject.connectSlotsByName(AutoWindow)
    # setupUi

    def retranslateUi(self, AutoWindow):
        AutoWindow.setWindowTitle(QCoreApplication.translate("AutoWindow", u"MainWindow", None))
    # retranslateUi

