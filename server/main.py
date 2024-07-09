from fastapi import (
    FastAPI, 
    Request,
    Response
)
from fastapi.middleware.cors import CORSMiddleware
from functools import lru_cache
import uvicorn
from socketio import AsyncServer, ASGIApp
from socketio.exceptions import ConnectionRefusedError

from room_manager import RoomManager
from session_manager import SessionManager
from config import Settings

# built-in libraries
import random
import string
from uuid import uuid4
import json

# temp imports
from fastapi.responses import HTMLResponse
from test2 import html

@lru_cache
def get_settings():
    return Settings()
settings: Settings = get_settings()

# setup socketio
sio = AsyncServer(cors_allowed_origins=[], async_mode="asgi")
socket_app = ASGIApp(sio)

# setup fastapi app
app = FastAPI()
# Cors middleware setup
origins = [
    "http://localhost:4200", #frontend url
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/socket.io", socket_app)

# session and room managers
room_manager = RoomManager()
session_manager = SessionManager()

'''
To connect 1st time:
1. host a room
    a. get a room id
    b. make a username
2. create_session(room_id) to create and get session_id
3. setup socket with session_id 
4. connect socket and join room

To reconnect from a disconnect:

'''

# @app.get("/")
# async def get():
#     return HTMLResponse(html)
#     # return {"message": "Hello World!"}

# @app.get("/api/rooms")
# async def get_rooms():
#     rooms = room_manager.get_rooms()
#     return {"rooms": rooms}

@app.get("/api/valid_room")
async def valid_room(room_id):
    return room_manager.is_valid_room(room_id)

@app.get("/api/create_session/")
async def create_session(request: Request):
    # Create a session id to identify each client
    session_id = request.cookies.get("session_id")
    room_id = request.query_params.get("room_id")
    if not session_id or not session_manager.get_session_id_exists(session_id):
        # session_id = str(uuid4())
        session_id = session_manager.create_session(room_id)
        response = Response(content=json.dumps({"session_id": session_id, "room_id": room_id, "reconnect": False}), media_type="application/json")
        response.set_cookie(key="session_id", value=session_id, httponly=True)
        return response
    return {"session_id": session_id, "room_id": session_manager.get_session(session_id)["room_id"], "reconnect": True}

@app.get("/api/get_session/")
async def get_session(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id or not session_manager.get_session_id_exists(session_id):
        response = Response(content=json.dumps({"session_id": None, "room_id": None, "reconnect": False}), media_type="application/json")
        response.delete_cookie(key="session_id", httponly=True)
        return response
    return {"session_id": session_id, "room_id": session_manager.get_session(session_id)["room_id"], "reconnect": True}

@app.get("/api/create_room_id")
async def create_room_id():
    room_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=settings.room_id_length))
    rooms = room_manager.get_rooms()
    while room_id in rooms:
        room_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=settings.room_id_length))
    return {"room_id": room_id}

@app.get("/api/is_host")
async def is_host(session_id: str):
    return False

'''
    Socketio events
'''

def getRoom(sid):
    return list(set(sio.manager.get_rooms(sid, "/")).difference({sid}))[0]

@sio.event
async def connect(sid, environ, auth):
    print("connect ", sid)
    session_id = auth['session_id']
    session = session_manager.get_session(session_id)
    # if not room_manager.get_room(session["room_id"]):
    #     room_manager.create_room(session["room_id"])
    if not session:
        raise ConnectionRefusedError('authentication failed')
    print(auth)

@sio.event
async def chat_message(sid, data):
    message = data['message']
    print("Chatting", sid, ":")
    room_id = getRoom(sid)
    room = room_manager.get_room(room_id)
    if room:
        username = [conn["username"] for conn in room["curr_connections"].values() if conn["curr_sid"] == sid][0]
        await sio.emit('chat_message', {"room_id": room_id, "message": message, "username": username}, room=room_id)

@sio.event
async def disconnect(sid):
    # room_id = getRoom(sid)
    # await sio.leave_room(sid, room_id)
    print('disconnect ', sid)

@sio.event
async def send_players(room_id):
    room = room_manager.get_room(room_id)
    current = room["curr_connections"]
    usernames = [current[i]["username"] for i in current]
    # print("room send", usernames)
    await sio.emit("players", usernames)

@sio.event
async def join_room(sid, data):
    room_id = data["room_id"]
    session_id = data['session_id']
    username = data.get('username', 'Guest')
    room_manager.join_room(room_id, session_id, sid, username)
    await sio.enter_room(sid, room_id)

    print(f"User {username} joined room {room_id}")

    # Send a status response to the client
    await sio.emit("join_room_status", {"status": "success"}, room=room_id)
    await send_players(room_id)

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
    await send_players(room_id)
    print(f"User {session_id} left room {room_id}")

if __name__ == "__main__":
    uvicorn.run(app, host = "localhost", port = 8000, log_level='debug', access_log=True)