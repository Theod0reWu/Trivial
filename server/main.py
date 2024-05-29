from fastapi import (
    FastAPI, 
    Request,
    Response
)
from fastapi.middleware.cors import CORSMiddleware
from functools import lru_cache
import random
import string
from uuid import uuid4
import uvicorn
from socketEvents import socket_app
from room_manager import room_manager
from session_manager import session_manager
import json

from config import Settings

# temp imports
from fastapi.responses import HTMLResponse
from test2 import html

@lru_cache
def get_settings():
    return Settings()

settings: Settings = get_settings()

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/socket.io", socket_app)

@app.get("/")
async def get():
    return HTMLResponse(html)
    # return {"message": "Hello World!"}

@app.get("/api/rooms")
async def get_rooms():
    rooms = room_manager.get_rooms()
    return {"rooms": rooms}

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

# @app.websocket("/ws/{room_id}/")
# async def websocket_endpoint(
#     *,
#     # websocket: WebSocket,
#     room_id: str,
#     username: str
# ):
#     try:
#         await websocket.accept()
#         if room_id not in rooms:
#             rooms[room_id] = Room(room_id)
#         room = rooms[room_id]
        
#         session_id = None
#         if "session_id" in websocket.cookies:
#             session_id = websocket.cookies["session_id"]
#             print(f"connection established for {session_id} in room {room_id}") 
#             room.curr_connections.append(UserConnection(session_id, websocket, username))

#         while True:
#             data = await websocket.receive_text() # await recieving data
#             await room.send(data)

#             # More testing
#             await websocket.send_text(f"Session ID is: {session_id}")
#             await websocket.send_text(f"Message text was: {data}, for room ID: {room_id}, from user: {username}")

#     except WebSocketDisconnect:
#         if room_id in rooms:
#             room = rooms[room_id]
#             room.curr_connections.remove(websocket)
#             if len(room.curr_connections) == 0:
#                 del rooms[room_id]
#         print("Client disconnected")
    # except Exception as e:
    #     await websocket.close()

if __name__ == "__main__":
    uvicorn.run(app, host = "localhost", port = 8000, log_level='debug', access_log=True)