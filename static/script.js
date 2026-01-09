const socket = io();

const messages = document.getElementById("messages");
const input = document.getElementById("msg");
const typingDiv = document.getElementById("typing");
const themeToggle = document.getElementById("themeToggle");
const emojiPicker = document.getElementById("emojiPicker");
const emojiBtn = document.getElementById("emojiBtn");
const onlineUsersList = document.getElementById("onlineUsers");
const roomCodeText = document.getElementById("roomCodeText");
const copyRoomBtn = document.getElementById("copyRoomBtn");

// =====================
// Helpers
// =====================

function generateRoomCode() {
    const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
    let code = "";
    for (let i = 0; i < 6; i++) {
        code += chars[Math.floor(Math.random() * chars.length)];
    }
    return code;
}

// =====================
// User input
// =====================

let username = "";
while (!username) {
    username = prompt("Enter your username:");
}

let choice = prompt("Type NEW to create a room or JOIN to join a room:").toUpperCase();

let roomCode = "";
let password = "";

if (choice === "NEW") {
    roomCode = generateRoomCode();
    password = prompt("Set a room password:");
    alert("Room created!\nRoom Code: " + roomCode);
} else {
    roomCode = prompt("Enter room code:").toUpperCase();
    password = prompt("Enter room password:");
}

roomCodeText.innerText = roomCode;

// Join room
socket.emit("join_room", {
    username,
    room_code: roomCode,
    password
});

// Wrong password
socket.on("join_error", (msg) => {
    alert(msg);
    location.reload();
});

// =====================
// Copy room code
// =====================

copyRoomBtn.onclick = () => {
    navigator.clipboard.writeText(roomCode);
    copyRoomBtn.classList.add("success");

    setTimeout(() => {
        copyRoomBtn.classList.remove("success");
    }, 1200);
};

let typingTimeout;

// =====================
// Messaging
// =====================

function sendMsg() {
    if (input.value.trim() === "") return;

    socket.send({
        user: username,
        text: input.value
    });

    socket.emit("stop_typing");
    input.value = "";
}

socket.on("message", (data) => {
    const div = document.createElement("div");
    div.classList.add("message");

    if (data.user === username) {
        div.classList.add("my-message");
    } else {
        div.classList.add("other-message");
        const name = document.createElement("div");
        name.className = "username";
        name.innerText = data.user;
        div.appendChild(name);
    }

    const text = document.createElement("div");
    text.innerText = data.text;
    div.appendChild(text);

    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
});

// =====================
// Typing indicator
// =====================

input.addEventListener("input", () => {
    socket.emit("typing", username);

    clearTimeout(typingTimeout);
    typingTimeout = setTimeout(() => {
        socket.emit("stop_typing");
    }, 1200);
});

socket.on("typing", (user) => {
    typingDiv.innerText = `${user} is typing...`;
});

socket.on("stop_typing", () => {
    typingDiv.innerText = "";
});

// =====================
// Online users
// =====================

socket.on("online_users", (users) => {
    onlineUsersList.innerHTML = "";

    users.forEach(user => {
        const li = document.createElement("li");
        li.innerText = user === username ? `${user} (You)` : user;
        onlineUsersList.appendChild(li);
    });
});

// =====================
// Theme toggle
// =====================

themeToggle.onclick = () => {
    document.body.classList.toggle("light");

    const icon = themeToggle.querySelector(".icon");
    const label = themeToggle.querySelector(".label");

    if (document.body.classList.contains("light")) {
        icon.innerText = "☀️";
        label.innerText = "Light";
    } else {
        icon.innerText = "🌙";
        label.innerText = "Dark";
    }
};

// =====================
// Emoji Picker
// =====================

emojiBtn.onclick = () => {
    emojiPicker.classList.toggle("hidden");
};

function insertEmoji(emoji) {
    input.value += emoji;
    input.focus();
    emojiPicker.classList.add("hidden");
}
