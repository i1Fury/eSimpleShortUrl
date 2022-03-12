from PIL import ImageGrab
from pyperclip import paste, copy
import io
import requests
import keyboard
import re
from win10toast import ToastNotifier

toast = ToastNotifier()

HOST = 'https://elliotcs.dev'
HOTKEY = 'menu'


def check_clip():
    im = ImageGrab.grabclipboard()
    if im:
        bim = io.BytesIO()
        im.save(bim, 'png')
        bim.seek(0)
        resp = requests.post('/upload', files={'image': ('screenshot.png', bim, 'image/png')})
    else:
        if not (clip := paste()): return
        if re.match(r'(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})', clip):
            resp = requests.post(HOST + '/newurl?api=true', data={'url': clip})
        else:
            resp = requests.post(HOST + '/bin', data={'clip': clip})

    if resp.status_code != 200: return  # Rate limited
    copy(resp.text)
    toast.show_toast(
        'Clipboard has been uploaded!',
        'The url to your clipboard has been copied!',
        duration = 3,
        icon_path = "icon.ico",
        threaded = True,
    )


if __name__ == '__main__':
    keyboard.add_hotkey(HOTKEY, check_clip, suppress=True)
    keyboard.wait()
