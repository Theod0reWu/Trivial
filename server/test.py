# For Testing
html = """
    <!DOCTYPE html>
<html>
<head>
    <title>Socket.IO Chat</title>
    <script src="https://cdn.socket.io/4.0.1/socket.io.min.js"></script>
</head>
<body>
    <h1>Socket.IO Chat</h1>
    <input type="text" id="username" placeholder="Username">
    <input type="text" id="room_id" placeholder="Room Code">
    <button onclick="joinRoom()">Join Room</button>
    <button onclick="getRooms()">List Rooms</button>
    <br>
    <input type="text" id="message" placeholder="Type a message">
    <button onclick="sendMessage()">Send</button>
    <ul id="messages"></ul>
    <script>
        let socket = null;
        let session_id = null;
        async function init() {
            session_id = await getSessionId();
            socket = await io("http://localhost:8000", {
                auth: {
                    session_id: session_id,
                }
            });
            socket.on("connect", () => {
                console.log("Connected to server");
            });
            socket.on("chat_message", (data) => {
                const { username, message } = data;
                const li = document.createElement("li");
                li.textContent = `[${username}] ${message}`;
                document.getElementById("messages").appendChild(li);
            });
            socket.on("reconnect", (data) => {
                socket.emit("join_room", { room_id: data.room_id, username: data.username, session_id: data.session_id});
            });
        }

        init();

        function joinRoom() {
            const username = document.getElementById("username").value;
            const room_id = document.getElementById("room_id").value;
            socket.emit("join_room", { room_id: room_id, username: username, session_id: session_id });
        }

        function sendMessage() {
            const message = document.getElementById("message").value;
            socket.emit("chat_message", {message: message});
            document.getElementById("message").value = "";
        }

        async function getSessionId() {
            const response = await fetch("/api/session");
            const data = await response.json();
            return data.session_id;
        }

        function getRooms() {
            fetch('/api/rooms')
                     .then(response => response.json())
                     .then(data => {
                        console.log(data.rooms);
                     })
                     .catch(error => {
                         console.error('Error fetching session ID:', error);
                     });
        }
    </script>
</body>
</html>
    """