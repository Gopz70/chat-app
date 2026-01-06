from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

# Chat messages
@socketio.on('message')
def handle_message(msg):
    send(msg, broadcast=True)

# Typing indicator
@socketio.on('typing')
def handle_typing(user):
    emit('typing', user, broadcast=True, include_self=False)

@socketio.on('stop_typing')
def handle_stop_typing(user):
    emit('stop_typing', broadcast=True, include_self=False)

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=10000)

