const socket = io();
const messages = document.getElementById("messages");
const input = document.getElementById("msg");
const typingDiv = document.getElementById("typing");
const themeToggle = document.getElementById("themeToggle");

let username = "";
while (!username) {
    username = prompt("Enter your username:");
}

let typingTimeout;

// Send message
function sendMsg() {
    if (input.value.trim() === "") return;

    socket.send({
        user: username,
        text: input.value
    });

    socket.emit("stop_typing", username);
    input.value = "";
}

// Receive message
socket.on("message", function (data) {
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

// Typing detection
input.addEventListener("input", () => {
    socket.emit("typing", username);

    clearTimeout(typingTimeout);
    typingTimeout = setTimeout(() => {
        socket.emit("stop_typing", username);
    }, 1200);
});

// Show typing
socket.on("typing", (user) => {
    typingDiv.innerText = `${user} is typing...`;
});

// Hide typing
socket.on("stop_typing", () => {
    typingDiv.innerText = "";
});

// Enter key
input.addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendMsg();
});

// Theme toggle
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
