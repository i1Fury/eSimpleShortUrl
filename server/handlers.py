from random import choices
import os

class handler:

    banned_words = ('clean', 'bitch')
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
    length = 5

    def __init__(self):
        self.ids = {}
        self.urls = {}
        for id in os.listdir('static/urls'):
            with open('static/urls/' + id, 'r') as f:
                url = f.read()
                self.urls[id] = url
                self.ids[url] = id
                f.close()
    
    
    def gen_name(self):
        return ''.join(choices(self.chars, k=self.length))
    

    def gen_safe_name(self):
        while (name := self.gen_name()) in self.banned_words:
            pass
        return name
    

    def gen_unique_name(self, path, ext=''):
        while os.path.exists(path + '/' + (name := self.gen_safe_name()) + ext):
            pass
        return name


    def new(self, url):
        while (id := self.gen_unique_name('static/urls')) in self.ids:
            pass
        if url.find("http://") != 0 and url.find("https://") != 0:
            url = 'http://' + url
        self.urls[id] = url
        self.ids[url] = id
        with open('static/urls/' + id, 'w+') as f:
            f.write(url)
            f.close()
        return id
    

    def new_image(self, image):
        name = self.gen_unique_name('static/screenshots', '.png')
        image.save('static/screenshots/' + name + '.png')
        return name
    

    def new_bin(self, data):
        name = self.gen_unique_name('static/bin')
        with open('static/bin/' + name, 'w+') as f:
            f.write(data)
            f.close()
        return name


    def get_url(self, id):
        try:
            return self.urls[id]
        except KeyError:
            return None
    

    def get_id(self, url):
        try:
            return self.ids[url]
        except KeyError:
            return None
