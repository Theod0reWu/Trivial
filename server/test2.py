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
    <button onclick="hostRoom()">Host Room</button>
    <button onclick="leaveRoom()">Leave Room</button>
    <button onclick="getRooms()">List Rooms</button>
    <br>
    <input type="text" id="room_code" placeholder="Room Code">
    <button onclick="joinRoom()">Join Room</button>
    <br>
    <input type="text" id="message" placeholder="Type a message">
    <button onclick="sendMessage()">Send</button>
    <ul id="messages"></ul>
    <script>
        let socket = null;
        let session = null;
        let room_code = null;

        createRoomId().then(rid => {
            getSession(rid).then(s => {
                session = s;
                if (s.reconnect) {
                    joinRoom(s.room_id);
                }
            }).catch(error => {
                console.error('Error getting session');
            });
        });

        function init(room_id, callback) {
            createSession(document.getElementById("username").value, room_id).then(s => {
                session = s;
                console.log(session);
                socket = io("http://localhost:8000", {
                    auth: {
                        session_id: session.session_id,
                    }
                });
                socket.on("connect", () => {
                    console.log("Connected to server");
                    if (callback) callback();
                });
                socket.on("chat_message", (data) => {
                    const { username, message } = data;
                    const li = document.createElement("li");
                    li.textContent = `[${username}] ${message}`;
                    document.getElementById("messages").appendChild(li);
                });
            }).catch(error => {
                console.error('Error getting session:', error);
            });
        }

        function hostRoom() {
            createRoomId().then(rid => {
                const username = document.getElementById("username").value;
                init(rid, () => {
                    console.log(rid);
                    socket.emit("join_room", { room_id: rid, username: username, session_id: session.session_id });
                });
                room_code = rid;
            }).catch(error => {
                console.error('Error creating room:', error);
            });
        }

        function joinRoom(room_id=null) {
            const username = document.getElementById("username").value;
            let reconnect = false;
            if (!room_id) room_id = document.getElementById("room_code").value;
            else reconnect = true;
            getRooms().then(rooms => {
                if (!rooms.hasOwnProperty(room_id)) {
                    console.error("Error: Room " + room_id + " does not exist.");
                    return;
                }
                init(room_id, () => {
                    (reconnect) ?
                    socket.emit("rejoin_room", { room_id: room_id, session_id: session.session_id })
                    :
                    socket.emit("join_room", { room_id: room_id, username: username, session_id: session.session_id })
                });
                room_code = room_id;
            })
        }

        function leaveRoom() {
            if (socket) {
                socket.emit("leave_room", { room_id: room_code, session_id: session.session_id });
            }
            else {
                console.error("Socket is not connected");
            }
        }

        function createRoomId(room_id) {
            return fetch("/api/create_room_id")
                .then(response => response.json())
                .then(data => data.room_id)
                .catch(error => {
                    console.error('Error creating room:', error);
                });
        }

        function sendMessage() {
            const message = document.getElementById("message").value;
            if (socket) {
                socket.emit("chat_message", { message: message });
                document.getElementById("message").value = "";
            } else {
                console.error("Socket is not connected");
            }
        }

        function createSession(room_id) {
            return fetch(`/api/create_session?room_id=${room_id}`)
                .then(response => response.json())
                .then(data => {
                    console.log(data);
                    return data;
                })
                .catch(error => {
                    console.error('Error fetching session ID:', error);
                });
        }

        function getSession(room_id) {
            return fetch(`/api/get_session`)
                .then(response => response.json())
                .catch(error => {
                    console.error('Error fetching session ID:', error);
                });
        }

        function getRooms() {
            return fetch('/api/rooms')
                .then(response => response.json())
                .then(data => {
                    console.log(data.rooms);
                    return data.rooms;
                })
                .catch(error => {
                    console.error('Error fetching rooms:', error);
                });
        }
    </script>
</body>
</html>
    """