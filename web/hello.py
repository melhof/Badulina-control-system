
from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route('/')
def hello_world():
    context = {
        'name': 'taylor',
        'navigation': [
            {
                'href': '/',
                'caption': 'home',
            },
        ],
    }

    return render_template('hello.html', **context)
