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
socketio = SocketIO(app, )

robot = {}
map_database = "map_sqlite.db"
robot_database = "robots_sqlite.db"
BASE = "http://127.0.0.1:5000/"


def db_map_connection():
    conn_map = None
    conn_robot = None
    try:
        conn_map = sqlite3.connect(map_database, check_same_thread=False)
    except sqlite3.Error as e:
        print(e)
    return conn_map

def db_robot_connection():
    conn_map = None
    conn_robot = None
    try:
        conn_robot = sqlite3.connect(robot_database, check_same_thread=False)
    except sqlite3.Error as e:
        print(e)
    return conn_robot

conn_map = db_map_connection()
cur_map = conn_map.cursor()

conn_robot = db_robot_connection()
cur_robot = conn_robot.cursor()

@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)

@app.route('/robot', methods=['GET', 'POST'])
def all_robot():
    if flask.request.method == 'GET':
        cursor = cur_robot.execute("SELECT * FROM robots")

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

        cursor = cur_robot.execute(sql, (new_id, new_name, new_status, new_connection))
        conn_robot.commit()

        return f"Robot with the id: {cursor.lastrowid} created successfully"

@app.route('/robot/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def one_robot(id):
    if flask.request.method == 'GET':
        robot = None
        cursor = cur_robot.execute("SELECT * FROM robots WHERE ID={}".format(id))
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

        conn_robot.execute(sql, (name, status, connection, id))
        conn_robot.commit()
        return jsonify(updated_robot)

    if flask.request.method == 'DELETE':
        sql = """ DELETE FROM robots WHERE id=? """
        conn_robot.execute(sql, (id,))
        conn_robot.commit()

        return "The book with id: {} has been deleted".format(id), 200
    
@app.route('/map', methods=['GET', 'POST'])
def all_map():
    if flask.request.method == 'GET':
        cursor = cur_map.execute("SELECT * FROM map")

        maps = [
            dict(place=row[0], name=row[1])
            for row in cursor.fetchall()
        ]

        if maps is not None:
            return jsonify(maps)
    
    if flask.request.method == 'POST':
        new_place = request.form['Place']
        new_map_name = request.form['Map_name']

        sql = """INSERT INTO map (place, map_name)
                VALUES (?, ?)"""

        cursor = cur_map.execute(sql, (new_place, new_map_name))
        conn_map.commit()

        return f"Map with the id: {cursor.lastrowid} created successfully"

@app.route('/map/<place>', methods=['GET', 'PUT', 'DELETE'])
def one_map(place):
    if flask.request.method == 'GET':
        map = None
        cursor = cur_map.execute("SELECT * FROM map WHERE place={}".format(place))
        rows = cursor.fetchall()

        map = []

        for r in rows:
            map.append(r)

        if map is not None:
            return jsonify(map), 200
        else:
            abort(404, message="Something wrong")

    if flask.request.method == 'PUT':
        sql = """ UPDATE map
                SET map_name=?
                WHERE Place=? """
         
        map_name = request.form['Map_name']

        updated_map = {
            "Place": place,
            "Map_name": map_name
        }

        conn_map.execute(sql, (place, map_name))
        conn_map.commit()
        return jsonify(updated_map)

    if flask.request.method == 'DELETE':
        sql = """ DELETE FROM map WHERE Place=? """
        conn_map.execute(sql, (place,))
        conn_map.commit()

        return "The map with name: {} has been deleted".format(id), 200

@app.route('/map/download', methods=['GET'])
def download():
    if flask.request.method == 'GET':
        wget.download("http://127.0.0.1:5000/map")
        return "Map donwload", 200

@app.route('/robot/<name>/<command>', methods=['GET'])
def robot_command(name, command):
    if flask.request.method == 'GET':
        sid = robot[str(name)]
        data = "SID: " + sid + " have to do this command : " + command
        
        socketio.emit('command_to_do', command, to=sid)
        
        return data

@app.route('/robot/<name>/<position>', methods=['GET'])
def robot_position_to_reach(name, position):
    if flask.request.method == 'GET':
        sid = robot[str(name)]
        data = "SID: " + sid + " have to go there : " + position

        socketio.emit('position_to_reach', position, to=sid)

        return data

@socketio.on('connect')
def test_connect(auth):
    print(auth, 'Connected')
    username = request.sid
    room = request.sid
    join_room(room)
    socketio.send(username + ' has entered the room.', to=room)

    if "robot" in robot:
        robot[auth].append(request.sid)
    else :
        robot[auth] = request.sid
    
    sql = """ UPDATE robots 
            SET connection=?
            WHERE name=? """

    connection = "ON"

    conn_robot.execute(sql, (connection, auth))
    conn_robot.commit()


    print("Robot connected : ", get_robot_list())

@socketio.on('disconnect')
def test_disconnect():
    room = request.sid
    leave_room(room)
    print("Client leave room:" + request.sid)

    close_room(room)
    print("Room: ", room, " is closed.")
    
    name = None
    for key, value in list(robot.items()):
        if value == request.sid:
            # print("!!!!!! VAL : ", key)
            name = key
            del robot[key]

    sql = """ UPDATE robots 
            SET connection=?
            WHERE name=? """

    connection = "OFF"

    conn_robot.execute(sql, (connection, name))
    conn_robot.commit()

    print("Robot connected : ", get_robot_list())
    print('Client disconnected')

@socketio.on('ping')
def handle_message(data):
    print('received message: ' + str(data))

@socketio.on('check_map')
def handle_message(data):
    print("Processing Map Checking...")
    map_number = data[request.sid][0]
    if map_number == get_data(data):
        socketio.emit('good', to=request.sid)
    else:
        socketio.emit('download', "http://127.0.0.1:5000//map", to=request.sid)

@socketio.on('position')
def handle_message(data):
    print("Positon : ", data)

def get_data(data):
    # GOAL : return the SQL map name corresponding to the location of the robot 
    print("DATA from robot: ", data)

    cursor = cur_map.execute("SELECT * FROM map")

    maps = [
        dict(place=row[0], name=row[1])
        for row in cursor.fetchall()
    ]

    if maps is not None:
        print("SQL REQUEST : ", maps)

    for dict_ele in maps:
        if dict_ele['place'] == data[request.sid][1]:
            result = dict_ele['name']
            print('Chosen Element : ', dict_ele['name'])

    # Result is the name of the map which share the sme localisation a the data from the robot 
    return result

def get_robot_list():
    print(robot)

if __name__ == '__main__':
    socketio.run(app)