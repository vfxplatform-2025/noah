# -*- coding: utf-8 -*-
"""
frameless_window.py

Maya 2025(PySide6) 환경용 Frameless Window
"""

from os.path import join, dirname, abspath
from PySide6.QtCore import Qt, QMetaObject, Signal, Slot, QEvent
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QToolButton,
    QLabel, QSizePolicy
)

# stylesheet 파일 경로
_FL_STYLESHEET = join(dirname(abspath(__file__)), 'resources', 'frameless.qss')


class WindowDragger(QWidget):
    """ 윈도우 드래그 핸들러 """
    doubleClicked = Signal()

    def __init__(self, window: QWidget, parent: QWidget = None):
        super().__init__(parent)
        self._window = window
        self._mousePressed = False

    def mousePressEvent(self, event):
        self._mousePressed = True
        self._mousePos = event.globalPos()
        self._windowPos = self._window.pos()

    def mouseMoveEvent(self, event):
        if self._mousePressed:
            delta = event.globalPos() - self._mousePos
            self._window.move(self._windowPos + delta)

    def mouseReleaseEvent(self, event):
        self._mousePressed = False

    def mouseDoubleClickEvent(self, event):
        self.doubleClicked.emit()


class ModernWindow(QWidget):
    """ Frameless 스타일의 모던 윈도우 """
    def __init__(self, content_widget: QWidget, parent: QWidget = None):
        super().__init__(parent)
        self._w = content_widget
        self.setupUi()

        # 컨텐츠를 감싸는 레이아웃
        contentLayout = QHBoxLayout()
        contentLayout.setContentsMargins(0, 0, 0, 0)
        contentLayout.addWidget(self._w)
        self.windowContent.setLayout(contentLayout)

        # 타이틀 및 초기 크기/위치
        self.setWindowTitle(self._w.windowTitle())
        self.setGeometry(self._w.geometry())

        self.installEventFilter(self)  # close 이벤트 가로채기

    def setupUi(self):
        # 최상위 레이아웃
        self.vboxWindow = QVBoxLayout(self)
        self.vboxWindow.setContentsMargins(0, 0, 0, 0)

        # 프레임 위젯
        self.windowFrame = QWidget(self)
        self.windowFrame.setObjectName('windowFrame')
        self.vboxFrame = QVBoxLayout(self.windowFrame)
        self.vboxFrame.setContentsMargins(0, 0, 0, 0)

        # (타이틀바 구현은 필요 시 주석 해제)
        # self.titleBar = WindowDragger(self, self.windowFrame)
        # ...

        # 컨텐츠 영역
        self.windowContent = QWidget(self.windowFrame)
        self.vboxFrame.addWidget(self.windowContent)
        self.vboxWindow.addWidget(self.windowFrame)

        # 스타일시트 적용
        with open(_FL_STYLESHEET, 'r') as f:
            self.setStyleSheet(f.read())

        # 자동 슬롯 연결
        QMetaObject.connectSlotsByName(self)

    def eventFilter(self, source, event):
        # 부모 위젯 close 시 content_widget에도 close
        if event.type() == QEvent.Close:
            return self._w.close()
        return super().eventFilter(source, event)

    def setWindowTitle(self, title: str):
        super().setWindowTitle(title)
        # self.lblTitle.setText(title)  # 타이틀바 사용 시

    @Slot()
    def on_btnMinimize_clicked(self):
        self.setWindowState(Qt.WindowMinimized)

    @Slot()
    def on_btnRestore_clicked(self):
        self.btnRestore.setVisible(False)
        self.btnMaximize.setVisible(True)
        self.setWindowState(Qt.WindowNoState)

    @Slot()
    def on_btnMaximize_clicked(self):
        self.btnRestore.setVisible(True)
        self.btnMaximize.setVisible(False)
        self.setWindowState(Qt.WindowMaximized)

    @Slot()
    def on_btnClose_clicked(self):
        self.close()

    @Slot()
    def on_titleBar_doubleClicked(self):
        if getattr(self, 'btnMaximize', None) and self.btnMaximize.isVisible():
            self.on_btnMaximize_clicked()
        else:
            self.on_btnRestore_clicked()
