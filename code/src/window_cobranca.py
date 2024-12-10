# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'window_cobranca.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
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
from PySide6.QtWidgets import (QApplication, QComboBox, QFormLayout, QFrame,
    QGridLayout, QLabel, QMainWindow, QMenuBar,
    QProgressBar, QPushButton, QScrollArea, QSizePolicy,
    QSpacerItem, QStackedWidget, QStatusBar, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(744, 491)
        MainWindow.setMinimumSize(QSize(744, 491))
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout_2 = QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.stackedWidget_body = QStackedWidget(self.centralwidget)
        self.stackedWidget_body.setObjectName(u"stackedWidget_body")
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.gridLayout_3 = QGridLayout(self.page)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)

        self.gridLayout_3.addItem(self.verticalSpacer, 3, 1, 1, 1)

        self.comboBox_body_funcionario = QComboBox(self.page)
        self.comboBox_body_funcionario.setObjectName(u"comboBox_body_funcionario")

        self.gridLayout_3.addWidget(self.comboBox_body_funcionario, 1, 1, 2, 1)

        self.pushButton_body_relatorio_anexar = QPushButton(self.page)
        self.pushButton_body_relatorio_anexar.setObjectName(u"pushButton_body_relatorio_anexar")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_body_relatorio_anexar.sizePolicy().hasHeightForWidth())
        self.pushButton_body_relatorio_anexar.setSizePolicy(sizePolicy)
        self.pushButton_body_relatorio_anexar.setMinimumSize(QSize(0, 50))
        icon = QIcon()
        icon.addFile(u"../imgs/upload-icon.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_body_relatorio_anexar.setIcon(icon)
        self.pushButton_body_relatorio_anexar.setIconSize(QSize(48, 48))

        self.gridLayout_3.addWidget(self.pushButton_body_relatorio_anexar, 5, 1, 1, 1)

        self.label_body_funcionario_title = QLabel(self.page)
        self.label_body_funcionario_title.setObjectName(u"label_body_funcionario_title")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_body_funcionario_title.sizePolicy().hasHeightForWidth())
        self.label_body_funcionario_title.setSizePolicy(sizePolicy1)
        font = QFont()
        font.setFamilies([u"Tw Cen MT"])
        font.setPointSize(16)
        self.label_body_funcionario_title.setFont(font)
        self.label_body_funcionario_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_3.addWidget(self.label_body_funcionario_title, 0, 1, 1, 1)

        self.label_bodyrelatorio_title = QLabel(self.page)
        self.label_bodyrelatorio_title.setObjectName(u"label_bodyrelatorio_title")
        sizePolicy1.setHeightForWidth(self.label_bodyrelatorio_title.sizePolicy().hasHeightForWidth())
        self.label_bodyrelatorio_title.setSizePolicy(sizePolicy1)
        self.label_bodyrelatorio_title.setFont(font)
        self.label_bodyrelatorio_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_3.addWidget(self.label_bodyrelatorio_title, 4, 1, 1, 1)

        self.label_body_empresas_title = QLabel(self.page)
        self.label_body_empresas_title.setObjectName(u"label_body_empresas_title")
        self.label_body_empresas_title.setFont(font)
        self.label_body_empresas_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_3.addWidget(self.label_body_empresas_title, 0, 0, 1, 1)

        self.frame = QFrame(self.page)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_4 = QGridLayout(self.frame)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout_4.setContentsMargins(150, 0, 150, 0)
        self.pushButton_body_executar = QPushButton(self.frame)
        self.pushButton_body_executar.setObjectName(u"pushButton_body_executar")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.pushButton_body_executar.sizePolicy().hasHeightForWidth())
        self.pushButton_body_executar.setSizePolicy(sizePolicy2)
        self.pushButton_body_executar.setMinimumSize(QSize(156, 48))
        font1 = QFont()
        font1.setPointSize(12)
        font1.setBold(False)
        font1.setItalic(True)
        font1.setUnderline(False)
        self.pushButton_body_executar.setFont(font1)

        self.gridLayout_4.addWidget(self.pushButton_body_executar, 0, 0, 1, 1)


        self.gridLayout_3.addWidget(self.frame, 6, 1, 1, 1)

        self.scrollArea = QScrollArea(self.page)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 242, 163))
        self.gridLayout_6 = QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.stackedWidget_empresas = QStackedWidget(self.scrollAreaWidgetContents)
        self.stackedWidget_empresas.setObjectName(u"stackedWidget_empresas")
        self.page_3 = QWidget()
        self.page_3.setObjectName(u"page_3")
        self.gridLayout_7 = QGridLayout(self.page_3)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.label_empresas_aviso = QLabel(self.page_3)
        self.label_empresas_aviso.setObjectName(u"label_empresas_aviso")
        font2 = QFont()
        font2.setFamilies([u"Tw Cen MT"])
        font2.setPointSize(13)
        font2.setItalic(True)
        self.label_empresas_aviso.setFont(font2)
        self.label_empresas_aviso.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_7.addWidget(self.label_empresas_aviso, 0, 0, 1, 1)

        self.stackedWidget_empresas.addWidget(self.page_3)
        self.page_4 = QWidget()
        self.page_4.setObjectName(u"page_4")
        self.formLayout = QFormLayout(self.page_4)
        self.formLayout.setObjectName(u"formLayout")
        self.stackedWidget_empresas.addWidget(self.page_4)

        self.gridLayout_6.addWidget(self.stackedWidget_empresas, 0, 0, 1, 1)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout_3.addWidget(self.scrollArea, 1, 0, 6, 1)

        self.stackedWidget_body.addWidget(self.page)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.gridLayout_8 = QGridLayout(self.page_2)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.horizontalSpacer_2 = QSpacerItem(246, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_8.addItem(self.horizontalSpacer_2, 0, 3, 1, 1)

        self.frame_3 = QFrame(self.page_2)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_9 = QGridLayout(self.frame_3)
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.gridLayout_9.setContentsMargins(100, -1, 100, -1)
        self.progressBar = QProgressBar(self.frame_3)
        self.progressBar.setObjectName(u"progressBar")

        self.gridLayout_9.addWidget(self.progressBar, 0, 0, 1, 1)


        self.gridLayout_8.addWidget(self.frame_3, 4, 0, 1, 4)

        self.horizontalSpacer = QSpacerItem(246, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_8.addItem(self.horizontalSpacer, 0, 0, 1, 1)

        self.label_load_gif = QLabel(self.page_2)
        self.label_load_gif.setObjectName(u"label_load_gif")
        self.label_load_gif.setMaximumSize(QSize(192, 192))
        self.label_load_gif.setPixmap(QPixmap(u"../imgs/load.gif"))
        self.label_load_gif.setScaledContents(True)
        self.label_load_gif.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_8.addWidget(self.label_load_gif, 0, 1, 1, 1)

        self.label_load_title = QLabel(self.page_2)
        self.label_load_title.setObjectName(u"label_load_title")
        font3 = QFont()
        font3.setFamilies([u"Tw Cen MT"])
        font3.setPointSize(24)
        font3.setBold(False)
        font3.setItalic(True)
        self.label_load_title.setFont(font3)
        self.label_load_title.setTextFormat(Qt.TextFormat.PlainText)
        self.label_load_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_8.addWidget(self.label_load_title, 2, 1, 1, 1)

        self.line_2 = QFrame(self.page_2)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setMinimumSize(QSize(0, 5))
        self.line_2.setStyleSheet(u"background-color: rgb(85, 170, 255);")
        self.line_2.setLineWidth(0)
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_8.addWidget(self.line_2, 3, 0, 1, 4)

        self.stackedWidget_body.addWidget(self.page_2)

        self.gridLayout_2.addWidget(self.stackedWidget_body, 1, 0, 1, 1)

        self.gridLayout_header = QGridLayout()
        self.gridLayout_header.setObjectName(u"gridLayout_header")
        self.frame_2 = QFrame(self.centralwidget)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_5 = QGridLayout(self.frame_2)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.gridLayout_5.setContentsMargins(100, -1, 100, -1)
        self.label_header_logo = QLabel(self.frame_2)
        self.label_header_logo.setObjectName(u"label_header_logo")
        self.label_header_logo.setPixmap(QPixmap(u"../imgs/deltaprice-hori.png"))
        self.label_header_logo.setScaledContents(True)

        self.gridLayout_5.addWidget(self.label_header_logo, 0, 0, 1, 1)


        self.gridLayout_header.addWidget(self.frame_2, 0, 0, 1, 1)

        self.line = QFrame(self.centralwidget)
        self.line.setObjectName(u"line")
        self.line.setMinimumSize(QSize(0, 5))
        self.line.setStyleSheet(u"background-color: rgb(85, 170, 255);")
        self.line.setLineWidth(0)
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_header.addWidget(self.line, 2, 0, 1, 1)

        self.label_header_title = QLabel(self.centralwidget)
        self.label_header_title.setObjectName(u"label_header_title")
        font4 = QFont()
        font4.setFamilies([u"Tw Cen MT"])
        font4.setPointSize(26)
        font4.setBold(True)
        self.label_header_title.setFont(font4)
        self.label_header_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_header.addWidget(self.label_header_title, 1, 0, 1, 1)


        self.gridLayout_2.addLayout(self.gridLayout_header, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 744, 22))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        self.statusbar.setStyleSheet(u"background-color: rgb(85, 170, 255);")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.stackedWidget_body.setCurrentIndex(0)
        self.stackedWidget_empresas.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Cobran\u00e7a Autom\u00e1tica", None))
        self.pushButton_body_relatorio_anexar.setText("")
        self.label_body_funcionario_title.setText(QCoreApplication.translate("MainWindow", u"Funcion\u00e1rio respons\u00e1vel", None))
        self.label_bodyrelatorio_title.setText(QCoreApplication.translate("MainWindow", u"Relat\u00f3rio de vencidos", None))
        self.label_body_empresas_title.setText(QCoreApplication.translate("MainWindow", u"Empresas que deseja cobrar", None))
        self.pushButton_body_executar.setText(QCoreApplication.translate("MainWindow", u"Executar", None))
        self.label_empresas_aviso.setText(QCoreApplication.translate("MainWindow", u"Insira o relat\u00f3rio de vencidos", None))
        self.label_load_gif.setText("")
        self.label_load_title.setText(QCoreApplication.translate("MainWindow", u"Carregando...", None))
        self.label_header_logo.setText("")
        self.label_header_title.setText(QCoreApplication.translate("MainWindow", u"Cobran\u00e7a Autom\u00e1tica", None))
    # retranslateUi

