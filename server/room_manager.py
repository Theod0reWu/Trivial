from firebase_init import db
from firebase_admin import firestore
from session_manager import SessionManager
from typing import Callable

import random

class Room:
    def __init__(self, state: str = "pregame", curr_connections: list[str] = None, 
                 all_connections: set[str] = None):
        self.state = state
        self.curr_connections = curr_connections if curr_connections is not None else []
        self.all_connections = all_connections if all_connections is not None else []
    
    @staticmethod
    def from_dict(source):
        room = Room(**source)
        return room

    def to_dict(self):
        return {
            "state": self.state,
            "curr_connections": self.curr_connections,
            "all_connections": self.all_connections
        }

    def __repr__(self):
        return f"Room(\
                state={self.state}, \
                curr_connections={self.curr_connections}, \
                all_connections={self.all_connections}\
            )"

class RoomManager:
    '''
        handles firebase database connection for rooms

        Methods:
            create_room(room_id)
                - Creates an entry for room_id
            join_room(room_id, session_id, sid, username)
                - Creates an entry if room_id doesn't exist (in which case this session_id is the host)
                - adds session_id and sid to the room_id document
            leave_room(room_id, session_id)

    '''
    def __init__(self):
        self.rooms = db.collection('Rooms')
    
    def create_room(self, room_id: str):
        room_ref = self.rooms.document(room_id)
        room = Room()
        print("room creation", room)
        room_ref.set(room.to_dict())

    def join_room(self, room_id: str, session_id: str):
        room_ref = self.rooms.document(room_id)
        room = room_ref.get().to_dict()
        
        # room doesn't exist yet, create room
        if not room:
            self.create_room(room_id)
            print("new room", room_ref.get().to_dict())
            room = Room().to_dict()

            # the maker is the host
            room_ref.update({"host": session_id})

        # data held in the room
        if (session_id not in room["curr_connections"]): room["curr_connections"].append(session_id)
        if (session_id not in room["all_connections"]): room["all_connections"].append(session_id)
        room_ref.update({"curr_connections": room["curr_connections"], "all_connections": room["all_connections"]})
    
    def leave_room(self, room_id: str, session_id: str, session_manager: SessionManager) -> str:
        '''
            returns sid of current or newly elected host and the session_id of a new picker (if one is needed)
            returns None is either can't be done

        '''
        print(f"{session_id} left the room")
        room_ref = self.rooms.document(room_id)
        room = room_ref.get().to_dict()
        if room:
            if (session_id in room["curr_connections"]):
                room["curr_connections"].remove(session_id)
            if (not room["curr_connections"]):
                session_manager.delete_session_by_room_id(room_id)
                room_ref.delete()
            else:
                room_ref.update({"curr_connections": room["curr_connections"]})
                new_host = None
                new_picker = None
                # appoint a new host
                if (room["host"] == session_id):
                    new_host_data = sorted(session_manager.get_sessions(room["curr_connections"]), key=lambda s: s["timestamp"])[0]
                    room_ref.update({"host": new_host_data["session_id"]})
                    new_host = new_host_data["curr_sid"]

                # appoint a new picker
                if ("picker" in room and session_id == room["picker"] and room["state"] == "board"):
                    new_picker = random.choice(room["curr_connections"])
                    room_ref.update({"picker": new_picker})
                    # new_picker = session_manager.get_sid(new_picker)
                return new_host, new_picker
        return None, None
    
    def get_room_by_id(self, room_id: str) -> dict:
        room_ref = self.rooms.document(room_id)
        room = room_ref.get().to_dict()
        return room

    def is_host(self, room_id: str, session_id: str) -> bool:
        # returns if the session_id is the host of the room_id
        room_ref = self.rooms.document(room_id)
        room = room_ref.get().to_dict()
        return room["host"] == session_id

    def get_rooms(self) -> dict:
        return {doc.id: doc.to_dict() for doc in self.rooms.stream()}


        
