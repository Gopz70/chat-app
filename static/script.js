const socket = io();

// =====================
// DOM ELEMENTS
// =====================

const messages = document.getElementById("messages");
const input = document.getElementById("msg");
const typingDiv = document.getElementById("typing");
const themeToggle = document.getElementById("themeToggle");
const emojiPicker = document.getElementById("emojiPicker");
const emojiBtn = document.getElementById("emojiBtn");
const onlineUsersList = document.getElementById("onlineUsers");
const roomCodeText = document.getElementById("roomCodeText");
const copyRoomBtn = document.getElementById("copyRoomBtn");

// Reply elements
const replyPreview = document.getElementById("replyPreview");
const replyUserEl = document.getElementById("replyUser");
const replyTextEl = document.getElementById("replyText");
const cancelReplyBtn = document.getElementById("cancelReply");

// =====================
// STATE
// =====================

let replyTo = null;
let typingTimeout;

// =====================
// HELPERS
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
// USER + ROOM SETUP
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

socket.emit("join_room", {
    username,
    room_code: roomCode,
    password
});

// =====================
// COPY ROOM CODE (FIXED)
// =====================

copyRoomBtn.onclick = () => {
    navigator.clipboard.writeText(roomCode);
    copyRoomBtn.classList.add("success");
    setTimeout(() => copyRoomBtn.classList.remove("success"), 1200);
};

// =====================
// SEND MESSAGE (WITH REPLY)
// =====================

function sendMsg() {
    if (!input.value.trim()) return;

    socket.send({
        user: username,
        text: input.value,
        reply: replyTo
    });

    replyTo = null;
    replyPreview.classList.add("hidden");
    socket.emit("stop_typing");
    input.value = "";
}

// =====================
// RECEIVE MESSAGE
// =====================

socket.on("message", (data) => {
    const div = document.createElement("div");
    div.classList.add("message");

    div.classList.add(data.user === username ? "my-message" : "other-message");

    // Reply bubble
    if (data.reply) {
        const replyDiv = document.createElement("div");
        replyDiv.className = "reply-bubble";
        replyDiv.innerHTML = `<strong>${data.reply.user}</strong>${data.reply.text}`;
        div.appendChild(replyDiv);
    }

    if (data.user !== username) {
        const name = document.createElement("div");
        name.className = "username";
        name.innerText = data.user;
        div.appendChild(name);
    }

    const text = document.createElement("div");
    text.innerText = data.text;
    div.appendChild(text);

    // Reply button
    const replyBtn = document.createElement("button");
    replyBtn.innerText = "↩ Reply";
    replyBtn.style.background = "none";
    replyBtn.style.border = "none";
    replyBtn.style.color = "#22c55e";
    replyBtn.style.cursor = "pointer";
    replyBtn.style.marginTop = "6px";

    replyBtn.onclick = () => {
        replyTo = { user: data.user, text: data.text };
        replyUserEl.innerText = data.user;
        replyTextEl.innerText = data.text;
        replyPreview.classList.remove("hidden");
        input.focus();
    };

    div.appendChild(replyBtn);

    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
});

// =====================
// CANCEL REPLY
// =====================

cancelReplyBtn.onclick = () => {
    replyTo = null;
    replyPreview.classList.add("hidden");
};

// =====================
// TYPING INDICATOR
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
// ENTER KEY
// =====================

input.addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendMsg();
});

// =====================
// THEME TOGGLE (FIXED)
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
// EMOJI PICKER (FIXED)
// =====================

emojiBtn.onclick = () => {
    emojiPicker.classList.toggle("hidden");
};

function insertEmoji(emoji) {
    input.value += emoji;
    input.focus();
    emojiPicker.classList.add("hidden");
}

// =====================
// ONLINE USERS
// =====================

socket.on("online_users", (users) => {
    onlineUsersList.innerHTML = "";
    users.forEach(user => {
        const li = document.createElement("li");
        li.innerText = user === username ? `${user} (You)` : user;
        onlineUsersList.appendChild(li);
    });
});
