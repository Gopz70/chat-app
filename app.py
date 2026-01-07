from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode="threading")

# socket_id -> username
online_users = {}

@app.route('/')
def index():
    return render_template('index.html')

# =====================
# Chat messages
# =====================

@socketio.on('message')
def handle_message(msg):
    send(msg, broadcast=True)

# =====================
# User joins
# =====================

@socketio.on('join')
def handle_join(username):
    online_users[request.sid] = username
    emit('online_users', list(online_users.values()), broadcast=True)

# =====================
# User disconnects
# =====================

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in online_users:
        online_users.pop(request.sid)
        emit('online_users', list(online_users.values()), broadcast=True)

# =====================
# Typing indicator
# =====================

@socketio.on('typing')
def handle_typing(username):
    emit('typing', username, broadcast=True, include_self=False)

@socketio.on('stop_typing')
def handle_stop_typing(username):
    emit('stop_typing', broadcast=True, include_self=False)

# =====================
# Run app
# =====================

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(
        app,
        host="0.0.0.0",
        port=port,
        allow_unsafe_werkzeug=True
    )
