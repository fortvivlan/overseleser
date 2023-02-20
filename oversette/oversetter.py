from googletrans import Translator


def oversetter(text, src):
    '''main translating function'''
    if len(text) >= 5000:
        return 'LONG'
    translator = Translator()
    return translator.translate(text, src=src).text
