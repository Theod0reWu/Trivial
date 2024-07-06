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

    </script>
</body>
</html>
    """