import PyQt5.QtWidgets as qtwidgets
import PyQt5.QtGui as qtgui
import PyQt5.QtCore as qtcore

class DictWindow(qtwidgets.QWidget):
    '''A Window for getting the name from user'''
    choice = qtcore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Name your dictionary')
        self.setWindowIcon(qtgui.QIcon('oversette/resources/icons/book.ico'))
        self.liner = qtwidgets.QLineEdit(self)
        self.button = qtwidgets.QPushButton("&Default")
        self.button.setText('OK')
        self.button.clicked.connect(self.ok)
        self.button.setDefault(True)
        self.layout = qtwidgets.QHBoxLayout()
        self.layout.addWidget(self.liner)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)

    def ok(self):
        self.choice.emit(self.liner.text())
        self.close()

class DictBrowser(qtwidgets.QWidget):
    '''A GUI window for browsing dict'''
    def __init__(self, data, lang):
        self.data = data 
        super().__init__()
        self.setWindowTitle(f'Dictionary for {lang}')
        self.setWindowIcon(qtgui.QIcon('oversette/resources/icons/book.ico'))
        self.resize(900, 1200)
        self.layout = qtwidgets.QVBoxLayout()
        fontId = qtgui.QFontDatabase.addApplicationFont("oversette/resources/maiola.ttf")
        if fontId < 0:
            print('font not loaded')
        families = qtgui.QFontDatabase.applicationFontFamilies(fontId)
        self.font = qtgui.QFont(families[0], 12)
        self.dictlist = qtwidgets.QTableWidget()
        columns = ['Original', 'Translation']
        self.dictlist.setFont(self.font)
        self.dictlist.setRowCount(len(self.data))
        self.dictlist.setColumnCount(2)
        self.dictlist.setHorizontalHeaderLabels(columns)
        for idx, key in enumerate(sorted(self.data)):
            self.dictlist.setItem(idx, 0, qtwidgets.QTableWidgetItem(key))
            self.dictlist.setItem(idx, 1, qtwidgets.QTableWidgetItem(', '.join(sorted(self.data[key]))))
        self.dictlist.horizontalHeader().setStretchLastSection(True)
        self.dictlist.horizontalHeader().setSectionResizeMode(qtwidgets.QHeaderView.Stretch)
        self.dictlist.verticalHeader().setVisible(False)
        self.layout.addWidget(self.dictlist)
        self.setLayout(self.layout)