# Overseleser 0.9

(Oversette + leser)

This is a small GUI program to read books in foreign languages and to get interactive translations from Google Translate. I made it for my own use.

### Dependencies:

    googletrans==4.0.0-rc1
    beautifulsoup4
    EbookLib
    pdfminer.six
    python-docx

### What it can:

- Open files and display them as raw text, supported formats:
  - .txt, encoding: UTF-8
  - .epub
  - .pdf (beware: some pdfs are too heavy or contain images instead of OCR)
  - .docx
- Save currently opened file, chosen language, cursor position and font size
- Increase and decrease font size
- Convert supported formats to .txt and store in "books" folder
- You may choose source language out of ~ 15 languages
- Destination language will be most probably English
- You may copy selected text and paste it anywhere you want
- There are hotkeys!

### What it can't:

- run under MacOS. I hate macs, there will be no support ever
- open .djvu and .pdf with pics. I would have to do OCR for that...
- change font family (I was too lazy to find out how to add custom fonts, but I may do so in future)
- open .doc (who the f*ck uses .doc nowadays? Oh, and .rtf too, convert them yourselves)
- you may resize the window, but subwindow sizes are hardcoded and will stay the same. I may change this in future, but for now I'm content with the current size, anyway

### Will there ever be an .exe version?

I dunno, I'm too lazy