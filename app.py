from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit, join_room, leave_room
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode="threading")

# socket_id -> {username, room}
users = {}

# room_code -> password
room_passwords = {}

@app.route('/')
def index():
    return render_template('index.html')

# =====================
# Join room (with password)
# =====================

@socketio.on('join_room')
def handle_join(data):
    username = data['username']
    room = data['room_code']
    password = data['password']

    # Password validation
    if room in room_passwords:
        if room_passwords[room] != password:
            emit('join_error', 'Invalid room password')
            return
    else:
        room_passwords[room] = password

    users[request.sid] = {
        "username": username,
        "room": room
    }

    join_room(room)

    # 🔥 Always emit full updated list
    online = [u["username"] for u in users.values() if u["room"] == room]
    emit('online_users', online, room=room)

# =====================
# Request online users (SYNC FIX)
# =====================

@socketio.on('request_online_users')
def handle_request_online():
    user = users.get(request.sid)
    if not user:
        return

    room = user["room"]
    online = [u["username"] for u in users.values() if u["room"] == room]

    emit('online_users', online)

# =====================
# Messages
# =====================

@socketio.on('message')
def handle_message(msg):
    room = users.get(request.sid, {}).get("room")
    if room:
        send(msg, room=room)

# =====================
# Typing indicator
# =====================

@socketio.on('typing')
def handle_typing(username):
    room = users.get(request.sid, {}).get("room")
    if room:
        emit('typing', username, room=room, include_self=False)

@socketio.on('stop_typing')
def handle_stop_typing():
    room = users.get(request.sid, {}).get("room")
    if room:
        emit('stop_typing', room=room, include_self=False)

# =====================
# Disconnect
# =====================

@socketio.on('disconnect')
def handle_disconnect():
    user = users.pop(request.sid, None)
    if not user:
        return

    room = user["room"]
    leave_room(room)

    # Remove password if room is empty
    if not any(u["room"] == room for u in users.values()):
        room_passwords.pop(room, None)

    online = [u["username"] for u in users.values() if u["room"] == room]
    emit('online_users', online, room=room)

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
