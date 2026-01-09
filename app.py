from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit, join_room, leave_room
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode="threading")

# room_code -> { username : sid }
rooms = {}

# room_code -> password
room_passwords = {}

@app.route('/')
def index():
    return render_template('index.html')

# =====================
# Join room
# =====================

@socketio.on('join_room')
def handle_join(data):
    username = data['username']
    room = data['room_code']
    password = data['password']
    sid = request.sid

    # Password validation
    if room in room_passwords:
        if room_passwords[room] != password:
            emit('join_error', 'Invalid room password')
            return
    else:
        room_passwords[room] = password

    # Initialize room if needed
    if room not in rooms:
        rooms[room] = {}

    # 🔥 Overwrite any previous connection of same user
    rooms[room][username] = sid

    join_room(room)

    emit_online_users(room)

# =====================
# Emit online users (authoritative)
# =====================

def emit_online_users(room):
    if room not in rooms:
        return

    online = list(rooms[room].keys())
    emit('online_users', online, room=room)

# =====================
# Messages
# =====================

@socketio.on('message')
def handle_message(msg):
    room = get_user_room(request.sid)
    if room:
        send(msg, room=room)

# =====================
# Typing
# =====================

@socketio.on('typing')
def handle_typing(username):
    room = get_user_room(request.sid)
    if room:
        emit('typing', username, room=room, include_self=False)

@socketio.on('stop_typing')
def handle_stop_typing():
    room = get_user_room(request.sid)
    if room:
        emit('stop_typing', room=room, include_self=False)

# =====================
# Disconnect
# =====================

@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid

    for room in list(rooms.keys()):
        for user, stored_sid in list(rooms[room].items()):
            if stored_sid == sid:
                del rooms[room][user]

                if not rooms[room]:
                    rooms.pop(room)
                    room_passwords.pop(room, None)
                else:
                    emit_online_users(room)
                return

# =====================
# Helper: find user room
# =====================

def get_user_room(sid):
    for room, users in rooms.items():
        if sid in users.values():
            return room
    return None

# =====================
# Run
# =====================

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(
        app,
        host="0.0.0.0",
        port=port,
        allow_unsafe_werkzeug=True
    )
