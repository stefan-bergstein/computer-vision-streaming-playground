from flask_socketio import SocketIO
from flask import Flask, render_template, request

app = Flask(__name__)
sio = SocketIO(app, logger=True, engineio_logger=False)


#
# HTML Pages
#

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cam')
def cam():
    return render_template('cam.html')

@app.route('/avi')
def avi():
    return render_template('avi.html')


#
# From Cam/Screen to UI connections
#

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


@sio.on('cam2server', namespace='/cam')
def handle_cam_message(message):
    # print('Send msg to server2ui')
    sio.emit('server2ui', message, namespace='/ui')



#
# From Kafka-CV to AVI page connections
#

@sio.on('connect', namespace='/ui2')
def connect_ui2():
    print('ui2 client connected: {}'.format(request.sid))


@sio.on('disconnect', namespace='/ui2')
def disconnect_ui2():
    print('ui2 client disconnected: {}'.format(request.sid))


@sio.on('connect', namespace='/kcv')
def connect_kcv():
    print('[kcv client connected: {}'.format(request.sid))


@sio.on('disconnect', namespace='/kcv')
def disconnect_kcv():
    print('kcv client disconnected: {}'.format(request.sid))


@sio.on('kcv2server', namespace='/kcv')
def handle_kcv_message(message):
    sio.emit('server2ui2', message, namespace='/ui2')


if __name__ == "__main__":
    print('Starting server at http://localhost:8088')
    sio.run(app=app, host='0.0.0.0', port=8088)
