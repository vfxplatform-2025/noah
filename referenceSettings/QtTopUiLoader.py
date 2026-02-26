from PySide6 import QtCore
from PySide6.QtUiTools import QUiLoader

class UiLoader(QUiLoader):
    _baseinstance = None

    def createWidget(self, classname, parent=None, name=''):
        # 부모가 없고 _baseinstance 가 지정된 경우, baseinstance 자체를 widget 으로 사용
        if parent is None and self._baseinstance is not None:
            widget = self._baseinstance
        else:
            widget = super().createWidget(classname, parent, name)
            if self._baseinstance is not None:
                setattr(self._baseinstance, name, widget)
        return widget

    def loadUi(self, uifile, baseinstance=None):
        # baseinstance 설정
        self._baseinstance = baseinstance
        # load 메서드에 baseinstance 를 parent 로 넘겨줌
        widget = self.load(uifile, baseinstance)
        QtCore.QMetaObject.connectSlotsByName(widget)
        return widget
