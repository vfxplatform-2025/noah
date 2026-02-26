from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QFrame
import maya.cmds as cmds
import sys
import os

class ListEditor(QDialog):
    def __init__(self, items):
        super().__init__()
        self.file_path = cmds.file(sn=True, q=True)
        self.shot_full_name = os.path.basename(self.file_path)
        self.shot_name = os.path.splitext(self.shot_full_name)[0]
        self.items = items
        self.editedItems = []
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        maxLabelWidth = 200

        headerLayout = QHBoxLayout()
        changeBeforeLabel = QLabel('Outliner 이름')
        changeBeforeLabel.setFixedWidth(maxLabelWidth)
        headerLayout.addWidget(changeBeforeLabel)

        headerLayout.addWidget(QLabel('Export 이름'), 1)
        self.layout.addLayout(headerLayout)

        hLine = QFrame()
        hLine.setFrameShape(QFrame.HLine)
        hLine.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(hLine)

        self.lineEdits = []

        for item in self.items:
            rowLayout = QHBoxLayout()
            nameLabel = QLabel(item)
            nameLabel.setFixedWidth(maxLabelWidth)
            rowLayout.addWidget(nameLabel)

            vLine = QFrame()
            vLine.setFrameShape(QFrame.VLine)
            vLine.setFrameShadow(QFrame.Sunken)
            rowLayout.addWidget(vLine)

            exportNameLabel = QLabel("{0}_".format(self.shot_name))
            rowLayout.addWidget(exportNameLabel)
            lineEdit = QLineEdit()
            self.lineEdits.append(lineEdit)
            rowLayout.addWidget(lineEdit)

            self.layout.addLayout(rowLayout)

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
        self.editedItems = [lineEdit.text() for lineEdit in self.lineEdits]
        super().accept()

    def getEditedItems(self):
        return self.editedItems

if __name__ == "__main__":
    app = QApplication(sys.argv)
    initialList = sys.argv[1]
    editor = ListEditor(initialList)
    if editor.exec_():
        editedItems = editor.getEditedItems()
        print(editedItems)
    sys.exit(app.exec_())
