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
from game_generation.game import GameState
from session_manager import SessionManager
from game_manager import GameManager, BUZZ_IN_TIMER_NAME, ANSWER_TIMER_NAME
from config import Settings
from timer import run_timer

# built-in libraries
import random
import string
from uuid import uuid4
import json
import asyncio
import time
import os
import sys

ENVIRON_FRONTEND = "FRONTEND_URL"

@lru_cache
def get_settings():
    return Settings()
settings: Settings = get_settings()

# setup socketio
sio = AsyncServer(cors_allowed_origins=[], async_mode="asgi", ping_timeout=500, ping_interval=2500)
socket_app = ASGIApp(sio)

# setup fastapi app
app = FastAPI()
# Cors middleware setup
origins = [
    "http://localhost:4200", #frontend url
    "https://trivial-ai.vercel.app/",
    "https://trivial-challenge.vercel.app/"
]
if (ENVIRON_FRONTEND in os.environ):
    origins.append(os.environ[ENVIRON_FRONTEND])

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
game_manager = GameManager()

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

# @app.get("/api/rooms")
# async def get_rooms():
#     rooms = room_manager.get_rooms()
#     return {"rooms": rooms}

@app.get("/")
async def get():
    return {"message": "Hello World!"}

@app.get("/api/valid_room")
async def valid_room(room_id):
    return room_manager.is_valid_room(room_id)

@app.get("/api/create_session/")
async def create_session(request: Request):
    # Create a session id to identify each client
    session_id = request.cookies.get("session_id")
    room_id = request.query_params.get("room_id")
    username = request.query_params.get("username")
    if not session_id or not session_manager.get_session_id_exists(session_id):
        # session_id = str(uuid4())
        session_id = session_manager.create_session(room_id, username)
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
    session_data = session_manager.get_session(session_id)
    room_id = session_data["room_id"]
    room_data = room_manager.get_room_by_id(room_id)
    return { 
        "session_id": session_id, 
        "room_id": room_id, 
        "reconnect": True,
        "username": session_data["username"]
        }

@app.get("/api/create_room_id")
async def create_room_id():
    room_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=settings.room_id_length))
    rooms = room_manager.get_rooms()
    while room_id in rooms:
        room_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=settings.room_id_length))
    return {"room_id": room_id}

@app.get("/api/is_host")
async def is_host(session_id: str):
    room_id = session_manager.get_room_id(session_id)
    return {"is_host": room_manager.is_host(room_id, session_id)}

'''
    Socket.io events
'''

def get_ordered_players(players, session_info = False):
    if (not session_info):
        return sorted(session_manager.get_sessions(players), key=lambda s: s["timestamp"])
    return sorted(players, key=lambda s: s["timestamp"])   

async def send_players(room_id: str, room_data: str|None = None):
    if (room_data is None):
        room_data = room_manager.get_room_by_id(room_id)
    if (not room_data):
        return
    usernames = [i["username"] for i in get_ordered_players(room_data["curr_connections"])]
    await sio.emit("players", usernames, room=room_id)

async def send_game_state(room_id: str, state: str | None = None, sid: str | None = None):
    if (state is None):
        state = game_manager.get_game_state(room_id)
    if (sid is not None):
        await sio.emit("game_state", state, to=sid)
    else:
        await sio.emit("game_state", state, room=room_id)

async def send_board_data(room_id:str, room_data: dict|None = None, sid: str|None = None):
    '''
        Sends the list of category titles
        And a list of the prices of clues
    '''
    if (sid is not None):
        await sio.emit("board_data", game_manager.get_board_info(room_id, room_data), to=sid)
    else:
        await sio.emit("board_data", game_manager.get_board_info(room_id, room_data), room=room_id)

async def send_player_cash(room_id: str, room_data: dict|None = None, sid: str|None = None):
    if (room_data is None):
        room_data = room_manager.get_room_by_id(room_id)
    if (not room_data or "player_cash" not in room_data):
        return
    session_id = [i["session_id"] for i in get_ordered_players(room_data["curr_connections"])]
    cash = game_manager.get_player_cash(room_id, session_id, room_data)
    if (sid is not None):
        await sio.emit("player_cash", cash, to=sid)
    else:
        await sio.emit("player_cash", cash, room=room_id)

async def send_picker(room_id: str, picker_session_id: str|None = None):
    '''
        sends to the sid of the person who will pick
        also sends the index of the person to pick
    '''
    if (not picker_session_id):
        picker_session_id = game_manager.get_picker(room_id)
    sid = session_manager.get_sid(picker_session_id)
    await sio.emit("picker", True, to=sid)
    await sio.emit("picker", False, room=room_id, skip_sid=sid)
    room = room_manager.get_room_by_id(room_id)
    players = [i["session_id"] for i in get_ordered_players(room["curr_connections"])]
    await sio.emit("picker_index", players.index(picker_session_id), room=room_id)

async def send_picker_index(room_id: str, room_data: dict|None = None):
    if (room_data is None):
        room_data = room_manager.get_room_by_id(room_id)
    players = [i["session_id"] for i in get_ordered_players(room_data["curr_connections"])]
    await sio.emit("picker_index", players.index(game_manager.get_picker(room_id, room_data)), room=room_id)

async def send_picker_sid(room_id: str, session_id: str, sid: str, room_data: dict|None = None):
    '''
        Assumes that player with sid is not the picker (reconnecting players are no longer picker)
    '''
    if (room_data is None):
        room_data = room_manager.get_room_by_id(room_id)
    picker_session_id = game_manager.get_picker(room_id, room_data)
    # await sio.emit("picker", session_id == picker_session_id, to=sid)
    players = [i["session_id"] for i in get_ordered_players(room_data["curr_connections"])]
    await sio.emit("picker_index", players.index(picker_session_id), to=sid)

async def handle_leaving_room(room_id: str, session_id: str):
    '''
        Leaves the room in the database (handles things like the new host and new picker)
    '''
    host, picker = room_manager.leave_room(room_id, session_id, session_manager)
    if (host):
        await sio.emit("host", to=host)
    if (picker):
        await send_picker(room_id, picker)
    room_data = room_manager.get_room_by_id(room_id)
    await send_players(room_id, room_data)
    await send_player_cash(room_id, room_data)
    await send_picker_index(room_id, room_data)
    # needs handle sending player cash and if someone leaves in the clue game state

async def send_timer(room_id: str, timer_name: str, timer_data: dict = None):
    if (not timer_data):
        await sio.emit(timer_name, timer_data, room=room_id)
    await sio.emit(timer_name, room_manager.get_timer(room_id, timer_name), room=room_id)

@sio.event
async def connect(sid, environ, auth):
    print("connect ", sid)
    session_id = auth['session_id']
    session = session_manager.get_session(session_id)
    if not session:
        raise ConnectionRefusedError('authentication failed')
    else:
        room_data = room_manager.get_room_by_id(session['room_id'])
        if room_data and session_id in room_data['curr_connections']:
            raise ConnectionRefusedError('user already in room')
    session_manager.update_session(session_id, sid)

@sio.event
async def disconnect(sid):
    room = session_manager.get_room_by_sid(sid)
    if room:
        await handle_leaving_room(room["room_id"], room["session_id"])
    print('disconnect ', sid)

@sio.event
async def reconnect(sid, data):
    print("reconnecting", sid, data)
    room_id, session_id = data["room_id"], data["session_id"]
    room_data = room_manager.get_room_by_id(room_id)
    await send_players(room_id, room_data)
    if (room_data["state"] != GameState.PREGAME.value):
        await send_player_cash(room_id, room_data)
    if (room_data["state"] == GameState.BOARD.value or room_data["state"] == GameState.CLUE.value or room_data["state"] == GameState.ANSWERING.value):
        # await send_picker_sid(room_id, session_id, sid, room_data)
        await send_picker(room_id)
        await send_board_data(room_id, room_data, sid)
        await sio.emit("picked", game_manager.get_picked_clues(room_id), to=sid)
        await send_game_state(room_id, GameState.BOARD.value, sid)
        return
    # elif (room_data["state"] == GameState.CLUE.value):
    #     clue = GameManager.get_clue(room_data)
    #     duration = room_data[BUZZ_IN_TIMER_NAME]["end"] - room_data[BUZZ_IN_TIMER_NAME]["start"]
    #     await send_game_state(room_id, GameState.BOARD.value, sid)
    #     print("duration:",duration)
    #     await sio.emit("clue", {"clue": clue, "duration": duration}, to=sid)
    await send_game_state(room_id, room_data["state"], sid)

@sio.event
async def join_room(sid, data):
    room_id = data["room_id"]
    session_id = data['session_id']
    username = session_manager.get_username(session_id)
    room_manager.join_room(room_id, session_id)
    await sio.enter_room(sid, room_id)

    print(f"User {username} joined room {room_id}")

    # Send a status response to the client
    room_data = room_manager.get_room_by_id(room_id)
    if (room_data["state"] == GameState.PREGAME.value):
        await send_players(room_id)
    await sio.emit("join_room_status", {"status": "success"}, room=room_id)

@sio.event
async def rejoin_room(sid, data):
    room_id = data["room_id"]
    session_id = data["session_id"]
    # username = room_manager.get_room_by_id(room_id)["all_connections"][session_id]["username"]
    username = session_manager.get_username(session_id)

    room_manager.join_room(room_id, session_id)
    await sio.enter_room(sid, room_id)

    await sio.emit("rejoin_room_status", {"status": "success"}, room=room_id)

@sio.event
async def leave_room(sid, data):
    '''
        Expects data to be a dict with keys "room_id" and "session_id"
    '''
    room_id = data['room_id']
    session_id = data['session_id']

    await handle_leaving_room(room_id, session_id)

    # remove session and remove from sio room
    session_manager.delete_session(session_id)
    await sio.leave_room(sid, room_id)

    print(f"User {session_id} left room {room_id}")

@sio.event
async def get_game_state(sid, room_id):
    return room_manager.get_room_by_id(room_id)["state"]

@sio.event
async def get_categories(sid, data):
    return game_manager.get_game_categories(data["room_id"])

@sio.event
async def start_game(sid, data):
    room_id, session_id, num_categories, num_clues, given_categories = data["room_id"], data["session_id"], data["num_categories"], data["num_clues"], data["given_categories"]
    if (room_manager.is_host(room_id, session_id)):
        game_manager.set_game_state(room_id, GameState.LOADING)
        await send_game_state(room_id, GameState.LOADING.value)
        await game_manager.init_game_async(room_id, num_categories, num_clues, given_categories)
    else:
        return
    await send_picker(room_id)
    await send_board_data(room_id)
    await send_player_cash(room_id)
    await sio.emit("picked", game_manager.get_picked_clues(room_id), room=room_id)
    await send_game_state(room_id, GameState.BOARD.value)
    game_manager.start_game(room_id)

@sio.event
async def to_waiting(sid, data):
    room_id, session_id = data["room_id"], data["session_id"]
    if (room_manager.is_host(room_id, session_id)):
        game_manager.set_game_state(room_id, GameState.PREGAME)
        await sio.emit("switch_waiting", room=room_id)

### in-game events ####

async def finish_clue(room_id: str, display_ans: bool = True):
    room_data = None
    if (display_ans):
        answer, room_data = game_manager.get_correct_ans(room_id)
        await sio.emit("response", {"correct": True, "answer": answer, "end": True}, room=room_id);
        await sio.sleep(settings.response_show_time)
    # end game when all clues have been answered
    if (game_manager.check_game_over(room_id)):
        game_manager.end_game(room_id)
        await send_game_state(room_id, GameState.DONE.value)
    else:
        await sio.emit("picked", game_manager.get_picked_clues(room_id, room_data)[0], room=room_id)
        await send_picker(room_id)
        game_manager.set_game_state(room_id, GameState.BOARD)
        await send_game_state(room_id, GameState.BOARD.value)

async def end_answering(room_id: str, session_id: str = None):
    # if a session_id is given this means someone buzzed in and never answered/answered wrong
    game_manager.stop_answering(room_id)
    if (session_id):
        all_buzzed_in = game_manager.deduct_points(room_id, session_id)
        await send_player_cash(room_id)
        # if everyone buzzed in finish the clue (everyone was wrong)
        if (all_buzzed_in):
            await finish_clue(room_id, True)
            return

    # restart the buzz in timer and send open to new buzz-ins
    new_buzz_in_time = game_manager.restart_buzz_in_timer(room_id)
    await sio.emit("paused", {"action": "stop", "duration": new_buzz_in_time}, room=room_id)
    await run_timer(new_buzz_in_time, game_manager.check_buzz_in_timer, finish_clue, {"room_id": room_id})

@sio.event
async def board_choice(sid, data):
    '''
        Receives the picked clue card from the picker and sends out the clue to all the people in the room.
    '''
    room_id, session_id, category_idx, clue_idx = data["room_id"], data["session_id"], data["category_idx"], data["clue_idx"]
    clue = game_manager.pick(session_id, room_id, str(category_idx), str(clue_idx))
    if (clue is None):
        return

    # send chosen coords and then send the clue itself
    await sio.emit("picking", {"category_idx": category_idx, "clue_idx":clue_idx, "duration": settings.picked_time}, room=room_id)
    await asyncio.sleep(settings.picked_time)

    # start the timer for hitting the buzzer
    game_manager.init_buzz_in_timer(room_id, settings.buzz_in_time)
    await sio.emit("clue", {"clue": clue, "duration": settings.buzz_in_time}, room=room_id)
    await send_game_state(room_id, GameState.CLUE.value)

    await run_timer(settings.buzz_in_time, game_manager.check_buzz_in_timer, finish_clue, {"room_id": room_id}, {"room_id": room_id, "display_ans": True})
    
@sio.event
async def buzz_in(sid, data):
    '''
        someone buzzes in on a clue
    '''
    room_id, session_id = data["room_id"], data["session_id"]
    passed = game_manager.handle_buzz_in(room_id, session_id)
    if (not passed):
        return

    room = room_manager.get_room_by_id(room_id)
    sessions = session_manager.get_sessions(room["curr_connections"])
    players = get_ordered_players(sessions, True)
    buzzer_index, buzzer_sid = None, None
    for p in range(len(players)):
        if (players[p]['session_id'] == session_id):
            buzzer_index = p
            buzzer_sid = players[p]['curr_sid']

    #pause timer and let everyone know someone will be answering
    game_manager.pause_buzz_in_timer(room_id)
    game_manager.init_answer_timer(room_id, settings.answer_time)
    await sio.emit("answering", {"duration": settings.answer_time, "who": buzzer_index}, to=buzzer_sid)

    await sio.emit("paused", {"action": "start", "who": buzzer_index, "duration": settings.answer_time}, room=room_id, skip_sid=sid)
    await run_timer(settings.answer_time, game_manager.check_answer_timer, end_answering, {"room_id": room_id}, {"room_id": room_id, "session_id": session_id})

@sio.event
async def answer_clue(sid, data):
    room_id, session_id, answer = data["room_id"], data["session_id"], data["answer"].strip()

    good = False
    try:
        good = game_manager.handle_answer(room_id, session_id, answer)
    except ValueError as e:
        print(e)
        return

    if (good):
        # show the correct response and add points to the right person
        await sio.emit("response", {"correct": True, "answer": answer}, room=room_id);
        await send_player_cash(room_id)
        await sio.sleep(settings.response_show_time)

        await send_picker(room_id, session_id)
        # return to the board
        await finish_clue(room_id, False)
    else:
        # show the incorrect response
        await sio.emit("response", {"correct": False, "answer": answer}, room=room_id);
        await sio.sleep(settings.response_show_time)

        # restart the timer
        await end_answering(room_id, session_id)

if __name__ == "__main__":
    # uvicorn.run(app, host = "localhost", port = 8000, log_level='debug', access_log=True)
    uvicorn.run(app, host = "0.0.0.0", port=int(os.environ.get("PORT", 8000)), log_level='debug', access_log=True)