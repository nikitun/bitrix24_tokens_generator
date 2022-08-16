# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets
from ui_main_window import UiMainWindow

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = UiMainWindow()
    window.setWindowTitle('Битрикс24 Генератор Токенов')
    window.show()
    sys.exit(app.exec_())