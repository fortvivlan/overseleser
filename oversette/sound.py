from playsound import playsound 
from gtts import gTTS 
import os

class SoundPlayer:
    def __init__(self, lang):
        path = 'oversette/sound'
        if not os.path.exists(path):
            os.mkdir(path)
        self.filepath = os.path.join(path, 'current.mp3')
        self.lang = lang 

    def _getword(self, word):
        sound = gTTS(word, lang=self.lang)
        sound.save(self.filepath)
    
    def _playword(self):
        fullpath = os.path.abspath(self.filepath)
        playsound(fullpath)
        os.remove(self.filepath)

    def playsound(self, word):
        self._getword(word)
        self._playword()