import sys
import PyQt5.QtWidgets as qtwidgets
from PyQt5 import QtGui
from oversette.window import Window


def main():
    app = qtwidgets.QApplication(sys.argv)
    ex = Window()

    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()