# -*- coding: utf-8 -*-
"""
theme_loader.py

Maya 2025(PySide6) 환경에서 Dark/Light 테마를 적용하는 모듈
"""

from os.path import join, dirname, abspath
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QApplication

# 스타일시트 파일 경로
_STYLESHEET = join(dirname(abspath(__file__)), 'resources', 'style.qss')


def _apply_base_theme(app: QApplication):
    """기본 Fusion 스타일과 QSS를 적용합니다."""
    app.setStyle('Fusion')
    with open(_STYLESHEET, 'r') as f:
        app.setStyleSheet(f.read())


def dark(app: QApplication):
    """Dark 테마를 QApplication 인스턴스에 적용합니다."""
    p = QPalette()

    # 기본 색상 셋업
    p.setColor(QPalette.WindowText,       QColor(180, 180, 180))
    p.setColor(QPalette.Button,           QColor(53, 53, 53))
    p.setColor(QPalette.Light,            QColor(180, 180, 180))
    p.setColor(QPalette.Midlight,         QColor(90, 90, 90))
    p.setColor(QPalette.Dark,             QColor(35, 35, 35))
    p.setColor(QPalette.Text,             QColor(180, 180, 180))
    p.setColor(QPalette.BrightText,       QColor(180, 180, 180))
    p.setColor(QPalette.ButtonText,       QColor(180, 180, 180))
    p.setColor(QPalette.Base,             QColor(42, 42, 42))
    p.setColor(QPalette.Window,           QColor(53, 53, 53))
    p.setColor(QPalette.Shadow,           QColor(20, 20, 20))
    p.setColor(QPalette.Highlight,        QColor(42, 130, 218))
    p.setColor(QPalette.HighlightedText,  QColor(180, 180, 180))
    p.setColor(QPalette.Link,             QColor(56, 252, 196))
    p.setColor(QPalette.AlternateBase,    QColor(38, 38, 38))
    p.setColor(QPalette.ToolTipBase,      QColor(53, 53, 53))
    p.setColor(QPalette.ToolTipText,      QColor(180, 180, 180))

    # Disabled 상태 색상
    p.setColor(QPalette.Disabled, QPalette.WindowText,      QColor(127, 127, 127))
    p.setColor(QPalette.Disabled, QPalette.Text,            QColor(127, 127, 127))
    p.setColor(QPalette.Disabled, QPalette.ButtonText,      QColor(127, 127, 127))
    p.setColor(QPalette.Disabled, QPalette.Highlight,       QColor(80, 80, 80))
    p.setColor(QPalette.Disabled, QPalette.HighlightedText, QColor(127, 127, 127))

    app.setPalette(p)
    _apply_base_theme(app)


def light(app: QApplication):
    """Light 테마를 QApplication 인스턴스에 적용합니다."""
    p = QPalette()

    # 기본 색상 셋업
    p.setColor(QPalette.WindowText,       QColor(0, 0, 0))
    p.setColor(QPalette.Button,           QColor(240, 240, 240))
    p.setColor(QPalette.Light,            QColor(180, 180, 180))
    p.setColor(QPalette.Midlight,         QColor(200, 200, 200))
    p.setColor(QPalette.Dark,             QColor(225, 225, 225))
    p.setColor(QPalette.Text,             QColor(0, 0, 0))
    p.setColor(QPalette.BrightText,       QColor(0, 0, 0))
    p.setColor(QPalette.ButtonText,       QColor(0, 0, 0))
    p.setColor(QPalette.Base,             QColor(237, 237, 237))
    p.setColor(QPalette.Window,           QColor(240, 240, 240))
    p.setColor(QPalette.Shadow,           QColor(20, 20, 20))
    p.setColor(QPalette.Highlight,        QColor(76, 163, 224))
    p.setColor(QPalette.HighlightedText,  QColor(0, 0, 0))
    p.setColor(QPalette.Link,             QColor(0, 162, 232))
    p.setColor(QPalette.AlternateBase,    QColor(225, 225, 225))
    p.setColor(QPalette.ToolTipBase,      QColor(240, 240, 240))
    p.setColor(QPalette.ToolTipText,      QColor(0, 0, 0))

    # Disabled 상태 색상
    p.setColor(QPalette.Disabled, QPalette.WindowText,      QColor(115, 115, 115))
    p.setColor(QPalette.Disabled, QPalette.Text,            QColor(115, 115, 115))
    p.setColor(QPalette.Disabled, QPalette.ButtonText,      QColor(115, 115, 115))
    p.setColor(QPalette.Disabled, QPalette.Highlight,       QColor(190, 190, 190))
    p.setColor(QPalette.Disabled, QPalette.HighlightedText, QColor(115, 115, 115))

    app.setPalette(p)
    _apply_base_theme(app)
