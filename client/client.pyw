from PIL import ImageGrab
from pyperclip import paste, copy
import io
import requests
import keyboard
import re
from win10toast import ToastNotifier

toast = ToastNotifier()

SCHEME = 'https'
HOST = 'elliotcs.dev'
HOTKEY = 'ins'

class Memoize:
    def __init__(self, fn):
        self.fn = fn
        self.memo = {}
    def __call__(self, *args):
        if args not in self.memo:
            self.memo[args] = self.fn(*args)
        return self.memo[args]


@Memoize
def clip_handler(im, clip):
    if im:
        bim = io.BytesIO()
        im.save(bim, 'png')
        bim.seek(0)
        return requests.post(f'{SCHEME}://i.{HOST}/new', files={'image': ('screenshot.png', bim, 'image/png')})
    else:
        if not clip: return None
        if re.match(r'(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})', clip):
            return requests.post(f'{SCHEME}://u.{HOST}/new?api=true', data={'url': clip})
        else:
            return requests.post(f'{SCHEME}://bin.{HOST}/new', data={'clip': clip})


def check_clip():
    resp = clip_handler(ImageGrab.grabclipboard(), paste())
    if not resp: return
    elif resp.status_code != 200: return  # Rate limited
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
