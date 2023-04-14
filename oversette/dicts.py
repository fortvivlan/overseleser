import os
import pickle

class Dictionary:
    '''Dictionary Class: create dict, open dict, save dict, add word, print to txt'''
    def __init__(self, lang):
        self.path = '' 
        self.lang = lang
        self.data = {}

    def newdict(self, path):
        if not os.path.exists('dicts'):
            os.mkdir('dicts')
        self.path = os.path.join('dicts', path)
        if os.path.exists(self.path):
            self.opendict(self.path)
    
    def opendict(self, path):
        self.data = pickle.load(open(path, 'rb'))
        self.path = path

    def savedict(self):
        pickle.dump(self.data, open(self.path, 'wb'))

    def additem(self, entry, translation):
        if entry in self.data:
            if translation != "Google Translate doesn't respond" and translation not in self.data[entry]:
                self.data[entry].add(translation)
        else:
            self.data[entry] = {translation}
    
    def printdict(self):
        if not os.path.exists('dicts'):
            os.mkdir('dicts')
        with open(f'dicts/dict_{self.lang}.txt', 'w', encoding='utf8') as file:
            lkey = max([len(x) for x in self.data.keys()])
            lvalue = max([len(', '.join(x)) for x in self.data.values()])
            for key, value in sorted(self.data.items()):
                print(f"{key:<{lkey}} : {', '.join(sorted(value)):>{lvalue}}", file=file)
