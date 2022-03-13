from flask import Flask, request, Response, redirect, url_for, render_template, send_file
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from handlers import handler
import os
from passcode import g_passcode


DEBUG = False
HOST = 'elliotcs.dev'
SCHEME = 'https'


dirs = (
    'urls',
    'screenshots',
    'bin'
)

try:
    os.mkdir('static')
except FileExistsError:
    pass

for dir in dirs:
    try:
        os.mkdir('static/' + dir)
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
    return redirect(url_for('url_index'))


@app.route('/', subdomain='clean')
def cleaner_form():
    return render_template('clean.html')


@app.route('/', subdomain='clean', methods=['POST'])
def cleaner():
    passcode = request.form['pass']
    directive = request.form['directive'].lower()
    if passcode != g_passcode:
        return 'INVALID PASSCODE!'
    if directive not in ('all', 'bin', 'scs', 'urls'):
        return 'INVALID DIRECTIVE!'
    if directive == 'bin':
        path = 'bin'
    elif directive == 'scs':
        path = 'screenshots'
    elif directive == 'urls':
        path = 'urls'
    elif directive == 'all':
        for path in dirs:
            path = 'static/' + path
            for f in os.listdir(path):
                os.remove(os.path.join(path, f))
        return 'CLEANED ALL!'
    for f in os.listdir(path):
        os.remove(os.path.join(path, f))
    return 'CLEANED ' + path


@app.route('/', subdomain='u')
def url_index():
    return render_template('shortener.html')


@app.route('/new', subdomain='u', methods=['GET', 'POST'])
def new_url():
    print('DOING NEW TING')
    url = request.form['url']
    if id := shortener.get_id(url):
        return f'{SCHEME}://{id}-u.{HOST}/' if 'api' in request.args and request.args['api'] == 'true' else f'That url has already been shortened to {SCHEME}://{id}-u.{HOST}/'
    id = shortener.new(url)
    return f'{SCHEME}://{id}-u.{HOST}/' if 'api' in request.args and request.args['api'] == 'true' else f'The shortened url is {SCHEME}://{id}-u.{HOST}/'


@app.route('/', subdomain='<id>-u')
def get_url(id):
    url = shortener.get_url(id)
    if url:
        return redirect(url)
    else:
        return 'Url not found!'


@app.route('/new', subdomain='i', methods=['POST'])
def new_screenshot():
    im = request.files['image']
    path = shortener.new_image(im)
    return f'{SCHEME}://{path}-i.{HOST}/'


@app.route('/', subdomain='<image>-i')
def get_screenshot(image):
    screenshot = 'static/screenshots/' + image + '.png'
    if os.path.exists(screenshot):
        return send_file(screenshot)
    else:
        return 'Image not found!'


@app.route('/new', subdomain='bin', methods=['POST'])
def new_bin():
    data = request.form['clip']
    path = shortener.new_bin(data)
    return f'{SCHEME}://{path}-bin.{HOST}/'


@app.route('/', subdomain='<file>-bin')
def get_bin(file):
    path = 'static/' + dirs[2] + '/' + file
    if os.path.exists(path):
        with open(path) as f:
            return Response(f.read(), mimetype='text/plain')
    else:
        return 'File not found!'


if __name__ == '__main__':
    if DEBUG:
        app.run(port=80, debug=True)
    else:
        from waitress import serve
        serve(app, host=HOST, port=80)
