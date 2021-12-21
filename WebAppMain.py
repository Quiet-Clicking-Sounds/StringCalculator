import flask
from flask.helpers import url_for
from flask.templating import _default_template_ctx_processor
from flask import request, redirect

from flask_socketio import SocketIO
from flask_socketio import send, emit

from markupsafe import escape
from pathlib import Path
from os import name
# initialise application and socket
app = flask.Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
socketio.run(app)
from instrument import Instrument

@app.route('/')
def homepage():
    print("123")
    return flask.render_template('home.html')


@app.route('/string_calculator/')
def string_calculator():
    print("123")
    return flask.render_template('string_calculator.html')


@socketio.on("json")
def instrument_update_event(*args):
    print(args, 'onjs')
    #emit('responce', 'there', callback=callback_func)


@socketio.event
def instrument_updater(*args):
    print(args,'event')
    instrument = Instrument(**args[0])


    emit('responce', instrument.note_dictionary())


def callback_func():
    print('callback')


if __name__ == '__main__':
    pass
