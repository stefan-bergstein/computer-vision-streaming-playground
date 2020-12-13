from flask_socketio import SocketIO
from flask import Flask, render_template, request

app = Flask(__name__)
sio = SocketIO(app, logger=True, engineio_logger=False)


@app.route('/')
def index():
    return render_template('index.html')


@sio.on('connect', namespace='/ui')
def connect_ui():
    print('ui client connected: {}'.format(request.sid))


@sio.on('disconnect', namespace='/ui')
def disconnect_ui():
    print('ui client disconnected: {}'.format(request.sid))


@sio.on('connect', namespace='/cam')
def connect_cam():
    print('[Cam client connected: {}'.format(request.sid))


@sio.on('disconnect', namespace='/cam')
def disconnect_cam():
    print('Cam client disconnected: {}'.format(request.sid))


@sio.on('cam2server')
def handle_cam_message(message):
    sio.emit('server2ui', message, namespace='/ui')


if __name__ == "__main__":
    print('Starting server at http://localhost:8088')
    sio.run(app=app, host='0.0.0.0', port=8088)
