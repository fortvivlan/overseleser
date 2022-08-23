from googletrans import Translator


def oversetter(text, src):
    if len(text) >= 5000:
        return 'LONG'
    translator = Translator()
    return translator.translate(text, src=src).text
