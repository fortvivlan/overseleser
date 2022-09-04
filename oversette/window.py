import os
import pickle
import PyQt5.QtWidgets as qtwidgets
import PyQt5.QtGui as qtgui
import PyQt5.QtCore as qtcore
from functools import partial
from oversette.openfile import FileOpener
from oversette.oversetter import oversetter


LANGLIST = {'Icelandic': 'is', 'Norwegian': 'no', 'Swedish': 'sv', 'Danish': 'da', 'German': 'de', 'Dutch': 'nl', 
'Italian': 'it', 'Spanish': 'es', 'French': 'fr', 'Romanian': 'ro', 'Portuguese': 'pt', 
'Czech': 'cs', 'Polish': 'pl', 'Serbian': 'sr', 'Bulgarian': 'bg', 'Slovenian': 'sl', 
'Greek': 'el', 'Turkish': 'tr'}


class External(qtcore.QObject):
   finished = qtcore.pyqtSignal()
   converted = qtcore.pyqtSignal(str)

   def convert(self, filepath):
      global res
      opn = FileOpener(filepath)
      res = opn.ooopen()
      self.converted.emit(res)
      self.finished.emit()


class Window(qtwidgets.QMainWindow):
   def __init__(self, parent = None):
      super().__init__(parent)
      self.resize(1250, 600)
      wid = qtwidgets.QWidget(self)
      self.setCentralWidget(wid)
      grid = qtwidgets.QGridLayout()
      wid.setLayout(grid)

      self.setWindowTitle("Overseleser")
      self.setWindowIcon(qtgui.QIcon('oversette/icons/book.png'))
      self._createActions()
      self._createMenuBar()
      self._createToolBars()
      self.textarea = qtwidgets.QPlainTextEdit(self)
      # self.textarea.move(10, 60)
      # self.textarea.resize(900, 530)
      # self.textarea.setReadOnly(True)
      self.translation = qtwidgets.QPlainTextEdit(self)
      grid.addWidget(self.translation, 1, 2, 1, 3)
      grid.addWidget(self.textarea, 1, 1)
      # self.translation.move(920, 60)
      # self.translation.resize(320, 530)
      self.translation.setReadOnly(True)
      self._createContextMenu()
      self.path = None
      self.font = None
      self._getsaved()
      if not self.font:
         self.font = 12
      f = qtgui.QFont('Times', self.font)
      self.textarea.setFont(f)
      self.translation.setFont(f)

   def _createMenuBar(self):
      menuBar = self.menuBar()
      fileMenu = menuBar.addMenu('&File')
      fileMenu.addAction(self.openAction)
      fileMenu.addAction(self.saveAction)
      fileMenu.addAction(self.closeAction)
      editMenu = menuBar.addMenu('&Edit')
      editMenu.addAction(self.copyAction)
      editMenu.addAction(self.convertAction)
      viewMenu = menuBar.addMenu('&View')
      viewMenu.addAction(self.sizepAction)
      viewMenu.addAction(self.sizemAction)

   def _createToolBars(self):
      langToolBar = self.addToolBar("Language")
      self.combo = qtwidgets.QComboBox()
      langToolBar.addWidget(self.combo)
      self.combo.insertItems(1, list(LANGLIST.keys()))


   def _createActions(self):
      self.openAction = qtwidgets.QAction('&Open')
      self.openAction.setText('&Open')
      self.openAction.setShortcut(qtgui.QKeySequence.Open)
      self.openAction.triggered.connect(self.openFile)
      self.openAction.setIcon(qtgui.QIcon('oversette/icons/open.ico'))

      self.closeAction = qtwidgets.QAction('&Close')
      self.closeAction.setText('&Close')
      self.closeAction.setShortcut(qtgui.QKeySequence('Ctrl+W'))
      self.closeAction.triggered.connect(self.closeFile)
      self.closeAction.setIcon(qtgui.QIcon('oversette/icons/close.png'))

      self.copyAction = qtwidgets.QAction('&Copy')
      self.copyAction.setText('&Copy')
      self.copyAction.triggered.connect(self.copypaste)
      self.copyAction.setShortcut(qtgui.QKeySequence.Copy)
      self.copyAction.setIcon(qtgui.QIcon('oversette/icons/copy.png'))

      self.sizepAction = qtwidgets.QAction('&Font size +')
      self.sizepAction.setText('&Font size +')
      self.sizepAction.setShortcut(qtgui.QKeySequence.ZoomIn)
      self.sizepAction.triggered.connect(self.fontsizeplus)

      self.sizemAction = qtwidgets.QAction('&Font size -')
      self.sizemAction.setText('&Font size -')
      self.sizemAction.setShortcut(qtgui.QKeySequence.ZoomOut)
      self.sizemAction.triggered.connect(self.fontsizeminus)

      self.saveAction = qtwidgets.QAction('&Bookmark')
      self.saveAction.setText('&Bookmark')
      self.saveAction.setShortcut(qtgui.QKeySequence.Save)
      self.saveAction.triggered.connect(self.save)
      self.saveAction.setIcon(qtgui.QIcon('oversette/icons/bookmark.png'))

      self.convertAction = qtwidgets.QAction('&Convert')
      self.convertAction.setText('&Convert')
      self.convertAction.triggered.connect(self.saveastxt)
      self.convertAction.setIcon(qtgui.QIcon('oversette/icons/convert.png'))

      self.translAction = qtwidgets.QAction('&Translate')
      self.translAction.setText('&Translate')
      self.translAction.triggered.connect(self.translate)
      self.translAction.setShortcut(qtgui.QKeySequence('Ctrl+T'))
      self.translAction.setIcon(qtgui.QIcon('oversette/icons/google.png'))

   def _createContextMenu(self):
      self.textarea.setContextMenuPolicy(qtcore.Qt.ActionsContextMenu)
      self.textarea.addAction(self.translAction)

   def _preparetext(self, res):
      if res == 'Encoding':
         qtwidgets.QMessageBox.about(self, 'Error', 'Your encoding should be UTF-8')
      elif res == 'PDF error':
         qtwidgets.QMessageBox.about(self, 'Error', 'Couldn\'t open PDF')
      elif res == 'Unknown':
         qtwidgets.QMessageBox.about(self, 'Error', 'Sorry, Overseleser does not support this format')
      else:
         self.textarea.clear()
         self.textarea.insertPlainText(res)
         name = os.path.splitext(os.path.basename(self.path))[0]
         self.setWindowTitle(f"Overseleser: {name}")

   def createThread(self, filepath):
        thread = qtcore.QThread()
        worker = External()
        worker.moveToThread(thread)
        thread.started.connect(partial(worker.convert, filepath))
        worker.converted.connect(self._preparetext)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        return thread

   def openFile(self):
      filename = qtwidgets.QFileDialog.getOpenFileName()
      filepath = filename[0]
      if filepath:
         self.thread = self.createThread(filepath)
         self.thread.start()
         self.path = filepath
         # opn = FileOpener(filepath)
         # res = opn.ooopen()
         # if res == 'Encoding':
         #    qtwidgets.QMessageBox.about(self, 'Error', 'Your encoding should be UTF-8')
         # elif res == 'PDF error':
         #    qtwidgets.QMessageBox.about(self, 'Error', 'Couldn\'t open PDF')
         # elif res == 'Unknown':
         #    qtwidgets.QMessageBox.about(self, 'Error', 'Sorry, Overseleser does not support this format')
         # else:
         #    self.path = filepath
         #    self._preparetext(res)

   def closeFile(self):
      self.path = None
      self.textarea.clear()
      self.setWindowTitle("Overseleser")

   def translate(self):
      cursor = self.textarea.textCursor()
      text = cursor.selectedText()
      translation = oversetter(text, LANGLIST[self.combo.currentText()])
      if translation == 'LONG':
         qtwidgets.QMessageBox.about(self, 'Error', 'Your text is too long!')
      else:
         self.translation.clear()
         self.translation.insertPlainText(translation)

   def copypaste(self):
      self.textarea.copy()

   def _getsaved(self):
      if not os.path.exists('settings'):
         return 
      settings = pickle.load(open('settings', 'rb'))
      self.path = settings['filepath']

      if settings['filepath']:
         opn = FileOpener(settings['filepath'])
         res = opn.ooopen()
         if res == 'REMOVED':
            qtwidgets.QMessageBox.about(self, 'Warning', 'File has been removed or renamed')
            return
         self._preparetext(res)
         cursor = self.textarea.textCursor()
         cursor.setPosition(settings['cursor'])
         self.textarea.setTextCursor(cursor)

      self.combo.setCurrentText(settings['language'])
      self.font = settings['font']

   def save(self):
      settings = {'filepath': self.path, 'cursor': self.textarea.textCursor().position(), 'language': self.combo.currentText(), 'font': self.font}
      pickle.dump(settings, open('settings', 'wb'))

   def fontsizeplus(self):
      self.font += 1
      default_font = self.textarea.font()
      default_font.setPointSize(self.font)
      self.textarea.setFont(default_font)

   def fontsizeminus(self):
      self.font -= 1
      default_font = self.textarea.font()
      default_font.setPointSize(self.font)
      self.textarea.setFont(default_font)

   def saveastxt(self):
      if self.path.endswith('.txt'):
         return
      text = self.textarea.toPlainText()
      if not os.path.exists('books'):
         os.mkdir('books')
      self.path = f'books/{os.path.splitext(os.path.basename(self.path))[0]}.txt'
      with open(self.path, 'w', encoding='utf8') as file:
         file.write(text)