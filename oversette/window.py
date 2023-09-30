import os
import pickle
import PyQt5.QtWidgets as qtwidgets
import PyQt5.QtGui as qtgui
import PyQt5.QtCore as qtcore
from PyQt5.QtCore import pyqtSlot
from functools import partial
from oversette.openfile import FileOpener
from oversette.oversetter import oversetter
from oversette.dicts import Dictionary
from oversette.dictwindow import DictWindow, DictBrowser
from oversette.sound import SoundPlayer


# list of available languages
LANGLIST = {'Icelandic': 'is', 'Norwegian': 'no', 'Swedish': 'sv', 'Danish': 'da', 'German': 'de', 'Dutch': 'nl', 
'Italian': 'it', 'Spanish': 'es', 'French': 'fr', 'Romanian': 'ro', 'Portuguese': 'pt', 
'Czech': 'cs', 'Polish': 'pl', 'Serbian': 'sr', 'Bulgarian': 'bg', 'Slovenian': 'sl', 
'Greek': 'el', 'Turkish': 'tr'}


#style for text area
STYLESHEET_TEXT = """
   QWidget {
        background-image: url("oversette/resources/paper.jpg") repeat stretch stretch;
    }
"""

# style for notes and translation area
STYLESHEET_NOTE = """
   QWidget {
         background-image: url("oversette/resources/note.jpg") repeat stretch stretch;
      }
"""

class External(qtcore.QObject):
   '''A class for processing pdf and epub separately from GUI:
   if you don't have a separate thread for this, your OS will think that your program froze
   '''
   finished = qtcore.pyqtSignal()
   converted = qtcore.pyqtSignal(str) # this signal will carry the converted text

   def convert(self, filepath):
      global res
      opn = FileOpener(filepath)
      res = opn.ooopen()
      self.converted.emit(res)
      self.finished.emit()

class Window(qtwidgets.QMainWindow):
   '''Main Window class'''
   def __init__(self, parent = None):
      super().__init__(parent)
      self.settings = qtcore.QSettings('Alliot', 'Overseleser') # to remember window size and position
      self.resize(self.settings.value("size", qtcore.QSize(1250, 600))) # initial size
      self.move(self.settings.value("pos", qtcore.QPoint(50, 50))) # initial position
      self.filesize = 0
      # main widget
      wid = qtwidgets.QWidget(self)
      self.setCentralWidget(wid)
      # layout = grid
      grid = qtwidgets.QGridLayout()
      wid.setLayout(grid)

      self.setWindowTitle("Overseleser")
      self.setWindowIcon(qtgui.QIcon('oversette/resources/icons/book.png'))
      self.setStyleSheet('background-color: #efeae1;')
      # create actions, menus and toolbars
      self._createActions()
      self._createMenuBar()
      self._createToolBars()

      # setting up font family and size
      fontId = qtgui.QFontDatabase.addApplicationFont("oversette/resources/maiola.ttf")
      if fontId < 0:
         print('font not loaded')
      families = qtgui.QFontDatabase.applicationFontFamilies(fontId)
      # text area is for the book itself
      self.textarea = qtwidgets.QPlainTextEdit(self)
      self.textarea.setStyleSheet(STYLESHEET_TEXT)
      self.textarea.setReadOnly(True)
      # note area is for writing down notes - it's editable
      self.notearea = qtwidgets.QPlainTextEdit(self)
      self.notearea.setStyleSheet(STYLESHEET_NOTE)
      # translation area gets Google translations
      self.translation = qtwidgets.QPlainTextEdit(self)
      self.translation.setStyleSheet(STYLESHEET_NOTE)
      self.translation.setReadOnly(True)
      # filler is just a pic
      self.filler = qtwidgets.QLabel('Label')
      self.filler.setPixmap(qtgui.QPixmap("oversette/resources/book.png"))
      self.filler.setAlignment(qtcore.Qt.AlignCenter)
      # adding widgets to grid
      grid.addWidget(self.translation, 1, 2, 1, 4)
      grid.addWidget(self.textarea, 1, 1)
      grid.addWidget(self.notearea, 2, 1, 4, 1)
      grid.addWidget(self.filler, 2, 2, 4, 4)
      self._createContextMenu()
      # handling important attributes
      self.path = None  # path to book
      self.notes = '' # notes
      self.currentdict = None # dictionary
      self.font = None # font size
      # trying to get settings
      self._getsaved()
      if not self.font:
         self.font = 12
      f = qtgui.QFont(families[0], self.font)
      self.textarea.setFont(f)
      self.translation.setFont(f)
      self.notearea.setFont(f)
      self.notearea.setPlainText(self.notes)
      self.sound = SoundPlayer(LANGLIST[self.combo.currentText()])


   def _createMenuBar(self):
      '''Creating menus: File, Edit, View and Dictionaries'''
      menuBar = self.menuBar()
      fileMenu = menuBar.addMenu('&File')
      fileMenu.addAction(self.openAction)
      fileMenu.addAction(self.saveAction)
      fileMenu.addAction(self.closeAction)
      editMenu = menuBar.addMenu('&Edit')
      editMenu.addAction(self.copyAction)
      editMenu.addAction(self.convertAction)
      editMenu.addAction(self.delnoteAction)
      viewMenu = menuBar.addMenu('&View')
      viewMenu.addAction(self.sizepAction)
      viewMenu.addAction(self.sizemAction)
      viewMenu.addAction(self.scrollAction)
      dictMenu = menuBar.addMenu('&Dictionaries')
      dictMenu.addAction(self.createDictAction)
      dictMenu.addAction(self.openDictAction)
      dictMenu.addAction(self.saveDictAction)
      dictMenu.addAction(self.viewDictAction)
      dictMenu.addAction(self.printDictAction)

   def _createToolBars(self):
      '''Creating toolbars: Language, Dictionaries'''
      langToolBar = self.addToolBar("Language")
      self.combo = qtwidgets.QComboBox()
      self.percentage = qtwidgets.QLabel('0') # scroll percentage
      # spacer allows percentage to be shown on the right side
      spacer = qtwidgets.QWidget()
      spacer.setSizePolicy(qtwidgets.QSizePolicy.Expanding, qtwidgets.QSizePolicy.Expanding)
      langToolBar.addWidget(self.combo)
      self.combo.insertItems(1, list(LANGLIST.keys())) # setting up language choice
      dictToolBar = self.addToolBar("Dictionaries")
      dictToolBar.addAction(self.createDictAction)
      dictToolBar.addAction(self.openDictAction)
      dictToolBar.addAction(self.saveDictAction)
      dictToolBar.addAction(self.viewDictAction)
      dictToolBar.addAction(self.printDictAction)
      dictToolBar.addWidget(spacer)
      dictToolBar.addWidget(self.percentage)


   def _createActions(self):
      '''Creating actions'''
      # opening books
      self.openAction = qtwidgets.QAction('&Open')
      self.openAction.setText('&Open')
      self.openAction.setShortcut(qtgui.QKeySequence.Open)
      self.openAction.triggered.connect(self.openFile)
      self.openAction.setIcon(qtgui.QIcon('oversette/resources/icons/open.png'))

      # closing books
      self.closeAction = qtwidgets.QAction('&Close')
      self.closeAction.setText('&Close')
      self.closeAction.setShortcut(qtgui.QKeySequence('Ctrl+W'))
      self.closeAction.triggered.connect(self.closeFile)
      self.closeAction.setIcon(qtgui.QIcon('oversette/resources/icons/close.png'))

      # quite unneeded - for copying selected text
      self.copyAction = qtwidgets.QAction('&Copy')
      self.copyAction.setText('&Copy')
      self.copyAction.triggered.connect(self.copypaste)
      self.copyAction.setShortcut(qtgui.QKeySequence.Copy)
      self.copyAction.setIcon(qtgui.QIcon('oversette/resources/icons/copy.png'))

      # changing size
      self.sizepAction = qtwidgets.QAction('&Font size +')
      self.sizepAction.setText('&Font size +')
      self.sizepAction.setShortcut(qtgui.QKeySequence.ZoomIn)
      self.sizepAction.triggered.connect(self.fontsizeplus)

      self.sizemAction = qtwidgets.QAction('&Font size -')
      self.sizemAction.setText('&Font size -')
      self.sizemAction.setShortcut(qtgui.QKeySequence.ZoomOut)
      self.sizemAction.triggered.connect(self.fontsizeminus)

      # saving position in the book
      self.saveAction = qtwidgets.QAction('&Bookmark')
      self.saveAction.setText('&Bookmark')
      self.saveAction.setShortcut(qtgui.QKeySequence.Save)
      self.saveAction.triggered.connect(self.save)
      self.saveAction.setIcon(qtgui.QIcon('oversette/resources/icons/bookmark.png'))

      # convert to txt
      self.convertAction = qtwidgets.QAction('&Convert')
      self.convertAction.setText('&Convert')
      self.convertAction.triggered.connect(self.saveastxt)
      self.convertAction.setIcon(qtgui.QIcon('oversette/resources/icons/convert.png'))

      # send selection to Google
      self.translAction = qtwidgets.QAction('&Translate')
      self.translAction.setText('&Translate')
      self.translAction.triggered.connect(self.translate)
      self.translAction.setShortcut(qtgui.QKeySequence('Ctrl+T'))
      self.translAction.setIcon(qtgui.QIcon('oversette/resources/icons/google.png'))

      # unfortunately I'd have to re-write the whole logic to make it work on scrolling so it has to be updated
      self.scrollAction = qtwidgets.QAction('&Update scroll percentage')
      self.scrollAction.setText('&Update scroll percentage')
      self.scrollAction.triggered.connect(self.scroll_percentage)
      self.scrollAction.setShortcut(qtcore.Qt.Key_F5)

      # delete notes
      self.delnoteAction = qtwidgets.QAction('&Clear notes')
      self.delnoteAction.setText('&Clear notes')
      self.delnoteAction.triggered.connect(self.clearnotes)
      self.delnoteAction.setShortcut(qtgui.QKeySequence.Delete)
      self.delnoteAction.setIcon(qtgui.QIcon('oversette/resources/icons/delete.png'))

      # get sound
      self.playsoundAction = qtwidgets.QAction('&Pronounce')
      self.playsoundAction.setText('&Pronounce')
      self.playsoundAction.triggered.connect(self.pronounce)
      self.playsoundAction.setIcon(qtgui.QIcon('oversette/resources/icons/pronounce.png'))

      # the following actions are for dictionaries
      self.createDictAction = qtwidgets.QAction('&Create new dictionary')
      self.createDictAction.setText('&Create new dictionary')
      self.createDictAction.triggered.connect(self.createDict)
      self.createDictAction.setIcon(qtgui.QIcon('oversette/resources/icons/newdict.png'))

      self.openDictAction = qtwidgets.QAction('&Open dictionary')
      self.openDictAction.setText('&Open dictionary')
      self.openDictAction.triggered.connect(self.openDict)
      self.openDictAction.setIcon(qtgui.QIcon('oversette/resources/icons/opendict.png'))

      self.saveDictAction = qtwidgets.QAction('&Save dictionary')
      self.saveDictAction.setText('&Save dictionary')
      self.saveDictAction.triggered.connect(self.saveDict)
      self.saveDictAction.setIcon(qtgui.QIcon('oversette/resources/icons/savedict.png'))

      self.viewDictAction = qtwidgets.QAction('&View dictionary')
      self.viewDictAction.setText('&View dictionary')
      self.viewDictAction.triggered.connect(self.viewDict)
      self.viewDictAction.setIcon(qtgui.QIcon('oversette/resources/icons/viewdict.png'))

      self.printDictAction = qtwidgets.QAction('&Create txt file')
      self.printDictAction.setText('&Create txt file')
      self.printDictAction.triggered.connect(self.printDict)
      self.printDictAction.setIcon(qtgui.QIcon('oversette/resources/icons/printdict.png'))

      self.addDictAction = qtwidgets.QAction('&Add to dictionary')
      self.addDictAction.setText('&Add to dictionary')
      self.addDictAction.triggered.connect(self.addWordtoDict)
      self.addDictAction.setShortcut(qtgui.QKeySequence('Ctrl+A'))
      self.addDictAction.setIcon(qtgui.QIcon('oversette/resources/icons/addword.png'))

   def _createContextMenu(self):
      '''Creating context menus: for translating and adding words to dict'''
      self.textarea.setContextMenuPolicy(qtcore.Qt.ActionsContextMenu)
      self.textarea.addAction(self.translAction)
      self.textarea.addAction(self.addDictAction)
      self.textarea.addAction(self.playsoundAction)

   def createDict(self):
      '''We create a dictionary'''
      self.dictWin = DictWindow() # the class for qlineedit to enter dict name
      self.dictWin.show()
      self.dictWin.choice.connect(self.receive_name)

   @pyqtSlot(str)
   def receive_name(self, choice):
      '''We receive dict name from user'''
      self.currentdict = Dictionary(self.combo.currentText())
      self.currentdict.newdict(choice)

   def openDict(self):
      '''Open an existing dict'''
      filename = qtwidgets.QFileDialog.getOpenFileName()
      filepath = filename[0]
      if filepath:
         self.currentdict = Dictionary(self.combo.currentText()) # a hole: if we open a dict for another language?
         self.currentdict.opendict(filename[0])

   def addWordtoDict(self):
      '''Adding word to dictionary'''
      if self.currentdict == None:
         qtwidgets.QMessageBox.about(self, 'Error', 'Open a dict first!')
         return 
      cursor = self.textarea.textCursor()
      text = cursor.selectedText()
      # not the best way to do it but else we may add a wrong translation or an empty string
      translation = oversetter(text, LANGLIST[self.combo.currentText()])
      if translation == '&LONG':
         qtwidgets.QMessageBox.about(self, 'Error', 'Your text is too long!')
      else:
         addword = self.currentdict.additem(text.strip().lower(), translation.lower())
         if addword:
            qtwidgets.QMessageBox.about(self, 'Error', 'Google error')

   def viewDict(self):
      '''Make GUI window for viewing your dict'''
      if self.currentdict != None and self.currentdict.data != {}:
         self.dictbrowser = DictBrowser(self.currentdict.data, self.combo.currentText())
         self.dictbrowser.show()
         self.dictbrowser.moddict.connect(self.receive_data)

   @pyqtSlot(dict)
   def receive_data(self, data):
      self.currentdict.data = data

   def saveDict(self):
      '''Saving bin'''
      if self.currentdict != None:
         self.currentdict.savedict()

   def printDict(self):
      '''printing dict to txt'''
      if self.currentdict != None and self.currentdict.data != {}:
         self.currentdict.printdict()

   def _preparetext(self, res):
      '''load book text to text area'''
      if res == 'Encoding':
         qtwidgets.QMessageBox.about(self, 'Error', 'Your encoding should be UTF-8')
      elif res == 'PDF error':
         qtwidgets.QMessageBox.about(self, 'Error', 'Couldn\'t open PDF')
      elif res == 'Unknown':
         qtwidgets.QMessageBox.about(self, 'Error', 'Sorry, Overseleser does not support this format')
      else:
         self.textarea.clear()
         self.textarea.insertPlainText(res)
         self.filesize = len(res)
         name = os.path.splitext(os.path.basename(self.path))[0]
         self.setWindowTitle(f"Overseleser: {name}")
         self.sound = SoundPlayer(LANGLIST[self.combo.currentText()])

   def createThread(self, filepath):
      '''create a thread for processing epub or pdf'''
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
      '''open a book'''
      filename = qtwidgets.QFileDialog.getOpenFileName()
      filepath = filename[0]
      if filepath:
         self.thread = self.createThread(filepath)
         self.thread.start()
         self.path = filepath

   def closeFile(self):
      '''close a book'''
      self.path = None
      self.textarea.clear()
      self.setWindowTitle("Overseleser")

   def translate(self):
      '''get translation'''
      cursor = self.textarea.textCursor()
      text = cursor.selectedText()
      translation = oversetter(text, LANGLIST[self.combo.currentText()])
      if translation == '&LONG':
         qtwidgets.QMessageBox.about(self, 'Error', 'Your text is too long!')
      else:
         self.translation.clear()
         self.translation.insertPlainText(translation)

   def pronounce(self):
      '''play sound'''
      cursor = self.textarea.textCursor()
      text = cursor.selectedText()
      self.sound.playsound(text)

   def copypaste(self):
      '''copy selection'''
      self.textarea.copy()

   def clearnotes(self):
      '''delete note text'''
      self.notes = ''
      self.notearea.setPlainText(self.notes)

   def scroll_percentage(self):
      '''compute scroll position'''
      # vsb = self.textarea.verticalScrollBar()
      cursorpos = self.textarea.textCursor().position()
      # ratio = round((vsb.value() / (vsb.maximum() or 1)) * 100, 2)
      ratio = round(cursorpos / (self.filesize or 1 ) * 100, 2)
      self.percentage.setText(str(ratio))

   def _getsaved(self):
      '''load settings: filepath to book, notes, language, dictpath and cursor position'''
      if not os.path.exists('settings'):
         return 
      settings = pickle.load(open('settings', 'rb'))
      self.path = settings['filepath']
      self.notes = settings['notes']
      self.currentdict = Dictionary(settings['language'])
      self.currentdict.opendict(settings['dictpath'])

      if settings['filepath']:
         opn = FileOpener(settings['filepath'])
         res = opn.ooopen()
         if res == 'REMOVED':
            qtwidgets.QMessageBox.about(self, 'Warning', 'File has been removed or renamed')
            return
         self._preparetext(res)
         # getting saved position in book text
         cursor = self.textarea.textCursor()
         cursor.setPosition(settings['cursor'])
         self.textarea.setTextCursor(cursor)
         self.scroll_percentage()

      self.combo.setCurrentText(settings['language'])
      self.font = settings['font']

   def save(self):
      '''save settings'''
      self.scroll_percentage()
      settings = {'filepath': self.path, 
                  'cursor': self.textarea.textCursor().position(), 
                  'language': self.combo.currentText(), 
                  'font': self.font, 
                  'notes': self.notearea.toPlainText(), 
                  'dictpath': self.currentdict.path}
      pickle.dump(settings, open('settings', 'wb'))

   def fontsizeplus(self):
      '''increase font size'''
      self.font += 1
      default_font = self.textarea.font()
      default_font.setPointSize(self.font)
      self.textarea.setFont(default_font)

   def fontsizeminus(self):
      '''decrease font size'''
      self.font -= 1
      default_font = self.textarea.font()
      default_font.setPointSize(self.font)
      self.textarea.setFont(default_font)

   def saveastxt(self):
      '''save book as txt'''
      if self.path.endswith('.txt'):
         return
      text = self.textarea.toPlainText()
      if not os.path.exists('books'):
         os.mkdir('books')
      self.path = f'books/{os.path.splitext(os.path.basename(self.path))[0]}.txt'
      with open(self.path, 'w', encoding='utf8') as file:
         file.write(text)

   def closeEvent(self, e):
      '''Write window size and position to config file'''
      self.saveDict()
      self.settings.setValue("size", self.size())
      self.settings.setValue("pos", self.pos())

      e.accept()