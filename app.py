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
# Join room with password
# =====================

@socketio.on('join_room')
def handle_join(data):
    username = data['username']
    room = data['room_code']
    password = data['password']

    # If room exists, check password
    if room in room_passwords:
        if room_passwords[room] != password:
            emit('join_error', 'Invalid room password')
            return
    else:
        # First user creates the room
        room_passwords[room] = password

    users[request.sid] = {
        "username": username,
        "room": room
    }

    join_room(room)

    emit(
        'online_users',
        [u["username"] for u in users.values() if u["room"] == room],
        room=room
    )

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
    if user:
        room = user["room"]
        leave_room(room)

        # Remove room password if empty
        if not any(u["room"] == room for u in users.values()):
            room_passwords.pop(room, None)

        emit(
            'online_users',
            [u["username"] for u in users.values() if u["room"] == room],
            room=room
        )

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
