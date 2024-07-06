from fastapi import (
    FastAPI, 
    Request,
    Response
)
from fastapi.middleware.cors import CORSMiddleware
from functools import lru_cache
import uvicorn
from socketEvents import socket_app, sio

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
2. create_session(username, room_id) to get session_id
3. 
'''

@app.get("/")
async def get():
    return HTMLResponse(html)
    # return {"message": "Hello World!"}

@app.get("/api/rooms")
async def get_rooms():
    rooms = room_manager.get_rooms()
    return {"rooms": rooms}

@app.get("/api/create_session")
async def get_session(username: str, room_id: str, request: Request):
    '''
       Create a session id to identify each client
       Session_id is stored with firebase, needs the room_id to create a session
       sessions are stored based upon room_id
    '''

    session_id = request.cookies.get("session_id")
    if not session_id or not session_manager.session_id_exists(session_id):
        session_id = session_manager.create_session(room_id)
        request.set_cookie(key="session_id", value=session_id, httponly=True)
        request.set_cookie(key="username", value=username, httponly=True)
    return {"session_id": session_id}

@app.get("/api/get_room")
async def get_room_id(request: Request):
    return {"room_id": request.cookies.get("session_id")};

@app.get("/api/delete_session/")
async def delete_session(request: Request):
    response.delete_cookie(key="session_id", httponly=True)
    response.delete_cookie(key="username", httponly=True)

@app.get("/api/create_room_id")
async def create_room_id():
    room_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=settings.room_id_length))
    rooms = room_manager.get_rooms()
    while room_id in rooms:
        room_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=settings.room_id_length))
    return {"room_id": room_id}

@app.get("/api/join_room")
async def join_room(sid, data):
    room_id = data["room_id"]
    session_id = data['session_id']
    username = data.get('username', 'Guest')

    room_manager.join_room(room_id, session_id, sid, username)
    await sio.enter_room(sid, room_id)

    print(f"User {username} joined room {room_id}")



if __name__ == "__main__":
    uvicorn.run(app, host = "localhost", port = 8000, log_level='debug', access_log=True)