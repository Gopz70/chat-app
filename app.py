from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit, join_room
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode="threading", cors_allowed_origins="*")

# room_code -> { sid : username }
rooms = {}

# room_code -> password
room_passwords = {}

@app.route('/')
def index():
    return render_template('index.html')

# =====================
# JOIN ROOM (MOBILE SAFE)
# =====================

@socketio.on('join_room')
def handle_join(data):
    username = data['username']
    room = data['room_code']
    password = data['password']
    sid = request.sid

    # Password check
    if room in room_passwords:
        if room_passwords[room] != password:
            emit('join_error', 'Invalid room password')
            return
    else:
        room_passwords[room] = password

    # Init room
    if room not in rooms:
        rooms[room] = {}

    # Join
    join_room(room)

    # 🔥 REMOVE any old SID with same username (mobile reconnect fix)
    for old_sid, old_user in list(rooms[room].items()):
        if old_user == username:
            del rooms[room][old_sid]

    rooms[room][sid] = username

    emit('system_message', f"🟢 {username} joined the room", room=room)
    emit_online_users(room)

# =====================
# MESSAGE
# =====================

@socketio.on('message')
def handle_message(msg):
    room = get_user_room(request.sid)
    if room:
        send(msg, room=room)

# =====================
# TYPING
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
# DISCONNECT (MOBILE SAFE)
# =====================

@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid

    for room in list(rooms.keys()):
        if sid in rooms[room]:
            username = rooms[room].pop(sid)

            emit('system_message', f"🔴 {username} left the room", room=room)

            if rooms[room]:
                emit_online_users(room)
            else:
                rooms.pop(room)
                room_passwords.pop(room, None)
            return

# =====================
# HELPERS
# =====================

def emit_online_users(room):
    users = list(set(rooms[room].values()))
    emit('online_users', users, room=room)

def get_user_room(sid):
    for room, users in rooms.items():
        if sid in users:
            return room
    return None

# =====================
# RUN
# =====================

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(
        app,
        host="0.0.0.0",
        port=port,
        allow_unsafe_werkzeug=True
    )
