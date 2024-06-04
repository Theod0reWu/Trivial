from socketio import AsyncServer, ASGIApp
from room_manager import room_manager
from session_manager import session_manager
from socketio.exceptions import ConnectionRefusedError

# class UserConnection:
#     def __init__(self, session_id, sid, username):
#         self.session_id = session_id
#         self.curr_sid = sid
#         self.username = username
#     def __eq__(self, other):
#         if isinstance(other, UserConnection):
#             return self.session_id == other.session_id
#         elif isinstance(other, str):
#             return self.session_id == other
#         return NotImplemented
#     def __hash__(self):
#         return hash(self.session_id)
        
# class Room:
#     def __init__(self, id):
#         self.id = id
#         self.curr_connections = [] # maintain order of connections
#         self.all_connections = set() # remember all connections
#     def updateConnections(self, session_id, sid, username):
#         try:
#             idx = self.curr_connections.index(session_id)
#             self.curr_connections[idx].curr_sid = sid
#         except ValueError:
#             self.curr_connections.append(UserConnection(session_id, sid, username))
#         try:
#             idx = self.all_connections.index(session_id)
#             self.all_connections[idx].curr_sid = sid
#         except ValueError:
#             self.all_connections.append(UserConnection(session_id, sid, username))
#     def getCurrConnection(self, **kwargs):
#         for conn in self.curr_connections:
#             if "sid" in kwargs and conn.curr_sid == kwargs["sid"] or "session_id" in kwargs and conn.session_id == kwargs["session_id"]:
#                 return conn
#         return None
#     def getConnection(self, **kwargs):
#         for conn in self.all_connections:
#             if "sid" in kwargs and conn.curr_sid == kwargs["sid"] or "session_id" in kwargs and conn.session_id == kwargs["session_id"]:
#                 return conn
#         return None

    # async def send(self, data):
    #     for conn in self.curr_connections:
    #         print(data) #test
    #         await conn.websocket.send_text(data)

sio = AsyncServer(cors_allowed_origins='*', async_mode="asgi")
socket_app = ASGIApp(sio)
# rooms: dict[str, Room] = {}

@sio.event
async def connect(sid, environ, auth):
    print("connect ", sid)
    session_id = auth['session_id']
    session = session_manager.get_session(session_id)
    # if not room_manager.get_room(session["room_id"]):
    #     room_manager.create_room(session["room_id"])
    if not session:
        raise ConnectionRefusedError('authentication failed')
        # print(session["room_id"])
        # username = room_manager.get_room(session["room_id"])["all_connections"][session_id].username
        # await sio.emit("reconnect", {"room_id": session["room_id"], "session_id": session_id})
    # for room_id, room in rooms.items():
    #     conn = room.getConnection(session_id=session_id)
    #     if conn is not None:
    #         await sio.emit("reconnect", {"room_id": room_id, "username": conn.username, "session_id": session_id})
    #         break
    print(auth)

@sio.event
async def chat_message(sid, data):
    message = data['message']
    print("Chatting", sid, ":")
    room_lst = list(set(sio.manager.get_rooms(sid, "/")).difference({sid}))
    room_id = room_lst[0]
    room = room_manager.get_room(room_id)
    if room:
        username = [conn["username"] for conn in room["curr_connections"].values() if conn["curr_sid"] == sid][0]
        await sio.emit('chat_message', {"room_id": room_id, "message": message, "username": username}, room=room_id)
    # if room_id in rooms:
    #     username = rooms[room_id].getCurrConnection(sid=sid).username
    #     await sio.emit('chat_message', {"room_id": room_id, "message": message, "username": username}, room=room_id) #skip_sid=sid

@sio.event
async def disconnect(sid):
    # room_lst = list(set(sio.manager.get_rooms(sid, "/")).difference({sid}))
    # room_id = room_lst[0]
    # await sio.leave_room(sid, room_id)
    print('disconnect ', sid)

@sio.event
async def join_room(sid, data):
    room_id = data["room_id"]
    session_id = data['session_id']
    username = data.get('username', 'Guest')

    # handle only allowing a user to join/belong to one room at a time
    # for room in rooms.values():
    #     if room.getConnection(session_id) is not None:
    #         return

    # if room_id not in rooms:
    #     rooms[room_id] = Room(room_id)
    # rooms[room_id].updateConnections(session_id, sid, username)
    room_manager.join_room(room_id, session_id, sid, username)
    await sio.enter_room(sid, room_id)

    print(f"User {username} joined room {room_id}")
    # Send a status response to the client
    await sio.emit("join_room_status", {"status": "success"}, room=room_id)

@sio.event
async def rejoin_room(sid, data):
    room_id = data["room_id"]
    session_id = data["session_id"]
    username = room_manager.get_room(room_id)["all_connections"][session_id]["username"]

    room_manager.join_room(room_id, session_id, sid, username)
    await sio.enter_room(sid, room_id)

    await sio.emit("rejoin_room_status", {"status": "success"}, room=room_id)

@sio.event
async def leave_room(sid, data):
    room_id = data['room_id']
    session_id = data['session_id']

    room_manager.leave_room(room_id, session_id)
    session_manager.delete_session(session_id)
    await sio.leave_room(sid, room_id)
    print(f"User {session_id} left room {room_id}")

    # if room_id in rooms:
    #     rooms[room_id].all_connections.remove(session_id)
    #     rooms[room_id].curr_connections.remove(session_id)
    #     print(f"User {username} left room {room_id}")