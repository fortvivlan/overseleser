from googletrans import Translator


def oversetter(text, src):
    '''main translating function'''
    if len(text) >= 5000:
        return '&LONG'
    translator = Translator()
    try:
        return translator.translate(text, src=src).text
    except Exception:
        return "Google Translate doesn't respond"
