import sqlite3
import flask
import requests
import json
import wget

from threading import Lock
from flask import Flask, render_template, session, request, \
    copy_current_request_context, jsonify, abort
from requests.api import get
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@socketio.on('connect')
def test_connect():
    print('Client Connected')

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

@socketio.on('ping')
def handle_message(data):
    print('received message: ' + str(data))

@socketio.on('message')
def handle_message(data):
    print('received message: ' + str(data))
    socketio.emit('server', "received")


if __name__ == '__main__':
    socketio.run(app)