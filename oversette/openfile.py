import os
from docx import Document
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from pdfminer.high_level import extract_text


class EpubReader:
    def __init__(self, path):
        self.path = path

    def reader(self):
        book = epub.read_epub(self.path)
        chapters = []
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                chapters.append(item.get_content())
        return chapters

    @staticmethod
    def chap2text(chap):
        blacklist = ['[document]', 'noscript', 'header', 'html', 'meta', 'head', 'input', 'script']
        output = ''
        soup = BeautifulSoup(chap, 'html.parser')
        text = soup.find_all(text=True)
        for t in text:
            if t.parent.name not in blacklist:
                output += f'{t} '
        return output

    def convert(self):
        res = ''
        chaps = self.reader()
        for chap in chaps:
            res += self.chap2text(chap)
        return res


class FileOpener:
    def __init__(self, path):
        self.path = path

    def txtread(self):
        try:
            with open(self.path, 'r', encoding='utf8') as file:
                return file.read()
        except:
            return 'Encoding'

    def docxread(self):
        doc = Document(self.path)
        text = ''
        for para in doc.paragraphs:
            text += para.text + '\n'
        return text

    def epubread(self):
        reader = EpubReader(self.path)
        return reader.convert()

    def pdfread(self):
        try:
            text = extract_text(self.path)
        except:
            return "PDF error"
        return text

    def ooopen(self):
        if not os.path.exists(self.path):
            return 'REMOVED'
        if self.path.endswith('.txt'):
            return self.txtread()
        elif self.path.endswith('.docx'):
            return self.docxread()
        elif self.path.endswith('.epub'):
            return self.epubread()
        elif self.path.endswith('.pdf'):
            return self.pdfread()
        else:
            return 'Unknown'