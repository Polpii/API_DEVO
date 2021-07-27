import socketio

sio = socketio.Client()

@sio.event
def connect():
    print('connection established')

# ACTIVATE WHEN MESSAGE RECEiVED FROM SERVER
@sio.event
def message(data):
    print('message received with ', data)

@sio.event
def disconnect():
    print('disconnected from server')

sio.connect('http://localhost:5000')
sio.emit('message', {'message': '1'})
sio.wait()