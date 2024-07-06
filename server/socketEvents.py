from socketio import AsyncServer, ASGIApp
from socketio.exceptions import ConnectionRefusedError

sio = AsyncServer(cors_allowed_origins=[], async_mode="asgi")
socket_app = ASGIApp(sio)

@sio.event
async def connect(sid, environ, auth):
    print("connect ", sid)
    session_id = auth['session_id']
    session = session_manager.get_session(session_id)
    if not session:
        raise ConnectionRefusedError('authentication failed')
    print(auth)

# @sio.event
# async def connect(sid):
#     print("connect", sid)

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

@sio.event
async def disconnect(sid):
    # room_lst = list(set(sio.manager.get_rooms(sid, "/")).difference({sid}))
    # room_id = room_lst[0]
    # await sio.leave_room(sid, room_id)
    print('disconnect ', sid)

# @sio.event
# async def join_room(sid, data):
#     room_id = data["room_id"]
#     session_id = data['session_id']
#     username = data.get('username', 'Guest')

#     # handle only allowing a user to join/belong to one room at a time
#     # for room in rooms.values():
#     #     if room.getConnection(session_id) is not None:
#     #         return

#     # if room_id not in rooms:
#     #     rooms[room_id] = Room(room_id)
#     # rooms[room_id].updateConnections(session_id, sid, username)
#     room_manager.join_room(room_id, session_id, sid, username)
#     await sio.enter_room(sid, room_id)

#     print(f"User {username} joined room {room_id}")
#     # Send a status response to the client
#     await sio.emit("join_room_status", {"status": "success"}, room=room_id)

# @sio.event
# async def rejoin_room(sid, data):
#     room_id = data["room_id"]
#     session_id = data["session_id"]
#     username = room_manager.get_room(room_id)["all_connections"][session_id]["username"]

#     room_manager.join_room(room_id, session_id, sid, username)
#     await sio.enter_room(sid, room_id)

#     await sio.emit("rejoin_room_status", {"status": "success"}, room=room_id)

# @sio.event
# async def leave_room(sid, data):
#     room_id = data['room_id']
#     session_id = data['session_id']

#     room_manager.leave_room(room_id, session_id)
#     session_manager.delete_session(session_id)
#     await sio.leave_room(sid, room_id)
#     print(f"User {session_id} left room {room_id}")

    # if room_id in rooms:
    #     rooms[room_id].all_connections.remove(session_id)
    #     rooms[room_id].curr_connections.remove(session_id)
    #     print(f"User {username} left room {room_id}")