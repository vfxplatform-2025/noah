# -*- coding:utf-8 -*-
from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QLabel,
    QPushButton, QHBoxLayout, QFrame, QComboBox
)
import maya.cmds as cmds
import sys
import os

class ListEditor(QDialog):
    def __init__(self, items):
        super().__init__()
        # 현재 신 파일 경로
        self.file_path = cmds.file(sn=True, q=True)
        self.shot_full_name = os.path.basename(self.file_path)
        self.shot_name = os.path.splitext(self.shot_full_name)[0]
        self.items = items
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        maxLabelWidth = 200

        # 헤더
        headerLayout = QHBoxLayout()
        changeBeforeLabel = QLabel('Outliner 이름')
        changeBeforeLabel.setFixedWidth(maxLabelWidth)
        headerLayout.addWidget(changeBeforeLabel)
        headerLayout.addWidget(QLabel('Export 이름'), 1)
        self.layout.addLayout(headerLayout)

        # 구분선
        hLine = QFrame()
        hLine.setFrameShape(QFrame.HLine)
        hLine.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(hLine)

        self.combo_boxes = []

        # 아이템별 행
        for item in self.items:
            rowLayout = QHBoxLayout()
            nameLabel = QLabel(item)
            nameLabel.setFixedWidth(maxLabelWidth)
            rowLayout.addWidget(nameLabel)

            vLine = QFrame()
            vLine.setFrameShape(QFrame.VLine)
            vLine.setFrameShadow(QFrame.Sunken)
            rowLayout.addWidget(vLine)

            exportNameLabel = QLabel(f"{self.shot_name}_")
            rowLayout.addWidget(exportNameLabel)

            comboBox = QComboBox()
            comboBox.addItems(["render", "prj", "plate", "shake"])
            self.combo_boxes.append(comboBox)
            rowLayout.addWidget(comboBox)

            self.layout.addLayout(rowLayout)

        # 버튼
        self.okButton = QPushButton("OK")
        self.okButton.clicked.connect(self.accept)
        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.reject)
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.cancelButton)
        buttonLayout.addWidget(self.okButton)
        self.layout.addLayout(buttonLayout)

        self.setLayout(self.layout)
        self.setWindowTitle('List Editor')

    def accept(self):
        self.editedItems = [cb.currentText() for cb in self.combo_boxes]
        super().accept()

    def getEditedItems(self):
        return getattr(self, 'editedItems', [])

if __name__ == "__main__":
    # Maya 내부에서는 이미 QApplication이 존재하므로 instance() 체크
    app = QApplication.instance() or QApplication(sys.argv)
    initialList = cmds.ls(selection=True) if len(sys.argv) < 2 else [sys.argv[1]]
    editor = ListEditor(initialList)
    if editor.exec():  # exec_() → exec()
        print(editor.getEditedItems())
    sys.exit(app.exec())  # exec_() → exec()
