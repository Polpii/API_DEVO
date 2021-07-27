import eventlet
import socketio

sio = socketio.Server()
app = socketio.WSGIApp(sio, static_files={
    '/': {'content_type': 'text/html', 'filename': 'index_test.html'}
})

robot = {}

@sio.event
def connect(sid, environ):
    print('connect ', sid)

@sio.event
def message(sid, data):
    print('message ', data['message'])
    sio.emit('message', data['message'], room=sid)
    
    data = {data['message']:sid}
    robot.update(data)

@sio.event
def disconnect(sid):
    print('disconnect ', sid)
    # del robot[sid]
    for key, value in list(robot.items()):
        if value == sid:
            del robot[key]


def show_robot_connected():
    print(robot)


if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)
    # while True:
    #     show_robot_connected()
