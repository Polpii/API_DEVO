import sqlite3
import flask

from threading import Lock
from flask import Flask, render_template, session, request, \
    copy_current_request_context, jsonify, abort
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect


# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='threading')
thread = None
thread_lock = Lock()


def db_connection():
    conn = None
    try:
        conn = sqlite3.connect("robots_sqlite.db", check_same_thread=False)
    except sqlite3.Error as e:
        print(e)
    return conn

conn = db_connection()
cur = conn.cursor()

def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        socketio.sleep(10)
        count += 1
        socketio.emit('my_response',
                      {'data': 'Server generated event', 'count': count})

@app.route('/')
def index():
    return render_template('real_index.html', async_mode=socketio.async_mode)

@app.route('/robot', methods=['GET', 'POST'])
def all_robot():
    if flask.request.method == 'GET':
        cursor = cur.execute("SELECT * FROM robots")

        robots = [
            dict(id=row[0], name=row[1], status=row[2], connection=row[3])
            for row in cursor.fetchall()
        ]

        if robots is not None:
            return jsonify(robots)
    
    if flask.request.method == 'POST':
        new_id = request.form['id']
        new_name = request.form['name']
        new_status = request.form['status']
        new_connection = request.form['connection']

        sql = """INSERT INTO robots (id, name, status, connection)
                VALUES (?, ?, ?, ?)"""

        cursor = cur.execute(sql, (new_id, new_name, new_status, new_connection))
        conn.commit()

        return f"Robot with the id: {cursor.lastrowid} created successfully"

@app.route('/robot/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def one_robot(id):
    if flask.request.method == 'GET':
        robot = None
        cursor = cur.execute("SELECT * FROM robots WHERE ID={}".format(id))
        rows = cursor.fetchall()

        robot = []

        for r in rows:
            robot.append(r)

        if robot is not None:
            return jsonify(robot), 200
        else:
            abort(404, message="Something wrong")

    if flask.request.method == 'PUT':
        sql = """ UPDATE robots 
                SET name=?, 
                    status=?,
                    connection=?
                WHERE id=? """
         
        name = request.form['name']
        status = request.form['status']
        connection = request.form['connection']


        updated_robot = {
            "id": id,
            "name": name,
            "status": status,
            "connection": connection
        }

        conn.execute(sql, (name, status, connection, id))
        conn.commit()
        return jsonify(updated_robot)

    if flask.request.method == 'DELETE':
        sql = """ DELETE FROM robots WHERE id=? """
        conn.execute(sql, (id,))
        conn.commit()

        return "The book with id: {} has been deleted".format(id), 200
    

@socketio.event
def my_event(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']})


@socketio.event
def my_broadcast_event(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         broadcast=True)


@socketio.event
def join(message):
    join_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': session['receive_count']})


@socketio.event
def leave(message):
    leave_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': session['receive_count']})


@socketio.on('close_room')
def on_close_room(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response', {'data': 'Room ' + message['room'] + ' is closing.',
                         'count': session['receive_count']},
         to=message['room'])
    close_room(message['room'])


@socketio.event
def my_room_event(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         to=message['room'])


@socketio.event
def disconnect_request():
    @copy_current_request_context
    def can_disconnect():
        disconnect()

    session['receive_count'] = session.get('receive_count', 0) + 1
    # for this emit we use a callback function
    # when the callback function is invoked we know that the message has been
    # received and it is safe to disconnect
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']},
         callback=can_disconnect)


@socketio.event
def my_ping():
    emit('my_pong')


@socketio.event
def connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected', request.sid)


if __name__ == '__main__':
    socketio.run(app)
