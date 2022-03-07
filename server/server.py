from flask import Flask, request, redirect, render_template, send_file, send_from_directory
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from handlers import handler
import os
import base64
from passcode import passcode

HOST = '127.0.0.1.nip.io'


dirs = (
    'urls',
    'screenshots',
    'bin'
)

for dir in dirs:
    try:
        os.mkdir(dir)
    except FileExistsError:
        pass

app = Flask(__name__, subdomain_matching=True)

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=['1 per second']
)

app.config["SERVER_NAME"] = HOST + ':80'

shortener = handler()


@app.route('/')
def index():
    return render_template('shortener.html')


@app.route('/', subdomain='clean')
def cleaner_form():
    return render_template('clean.html')


def get_passcode(bruh=passcode):
    if not bruh.startswith('BALLS'):
        return get_passcode(str(base64.b64decode(bruh), encoding='utf-8'))
    else:
        return str(base64.b64decode(bruh[5:]), encoding='utf-8')


@app.route('/clean', subdomain='clean', methods=['POST'])
def cleaner():
    passcode = request.form['pass']
    directive = request.form['directive'].lower()
    if passcode != get_passcode():
        return 'INVALID PASSCODE!'
    if directive not in ('bin', 'scs', 'urls'):
        return 'INVALID DIRECTIVE!'
    if directive == 'bin':
        path = 'bin'
    elif directive == 'scs':
        path = 'screenshots'
    elif directive == 'urls':
        path = 'urls'
    for f in os.listdir(path):
        os.remove(os.path.join(path, f))
    return 'CLEANED'


@app.route('/newurl', methods=['POST'])
def new_url():
    url = request.form['url']
    if id := shortener.get_id(url):
        return f'http://{HOST}/{id}' if 'api' in request.args and request.args['api'] == 'true' else f'That url has already been shortened to http://{HOST}/{id}'
    id = shortener.new(url)
    return f'http://{HOST}/{id}' if 'api' in request.args and request.args['api'] == 'true' else f'The shortened url is http://{HOST}/{id}'


@app.route('/<id>')
def redirect_route(id):
    url = shortener.get_url(id)
    if url:
        return redirect(url)
    else:
        return 'Url not found!'


@app.route('/upload', methods=['POST'])
def upload():
    im = request.files['image']
    path = shortener.new_image(im)
    return f'http://{path}.{HOST}/'


@app.route('/bin', methods=['POST'])
def bin():
    data = request.form['clip']
    path = shortener.new_bin(data)
    return f'http://{path}.bin.{HOST}/'


@app.route('/', subdomain='<file>.bin')
def get_bin(file):
    path = 'bin/' + file
    if os.path.exists(path):
        with open(path, 'r') as f: 
            return render_template('bin.html', text=f.read())
    else:
        return 'File not found!'


@app.route('/', subdomain='<image>')
def get_screenshot(image):
    screenshot = 'screenshots/' + image + '.png'
    if os.path.exists(screenshot):
        return send_file(screenshot)
    else:
        return 'Image not found!'


if __name__ == '__main__':
    from waitress import serve
    serve(app, host=HOST, port=80)
