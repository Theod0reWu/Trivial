from firebase_init import db
from firebase_admin import firestore
from typing import Callable

# class UserConnection:
#     def __init__(self, sid: str, username: str):
#         self.curr_sid = sid # socket.io session id
#         self.username = username
#         self.timestamp = firestore.SERVER_TIMESTAMP
    
#     @staticmethod
#     def from_dict(source):
#         conn = UserConnection(**source)
#         return conn

#     def to_dict(self):
#         return {
#             "curr_sid": self.curr_sid,
#             "username": self.username
#         }

#     def __repr__(self):
#         return f"UserConnection(\
#                 curr_sid={self.curr_sid}, \
#                 username={self.username}\
#             )"

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

    # def usernames(self):
    #     usernames = []
        # for i in self.curr_connections:
        #     usernames.append(self.curr_connections[i]["username"])
        # return usernames

    def __repr__(self):
        # return f"Room(\
        #         state={self.state}, \
        #         curr_connections={", ".join([session_id+": "+str(conn) for session_id, conn in self.curr_connections.items()])}, \
        #         all_connections={", ".join([session_id+": "+str(conn) for session_id, conn in self.all_connections.items()])}\
        #     )"
        return f"Room(\
                state={self.state}, \
                curr_connections={self.curr_connections}, \
                all_connections={self.all_connections}\
            )"

class RoomManager:
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
        print("room debugging!!!", room, room_id)
        if not room:
            self.create_room(room_id)
            print("new room", room_ref.get().to_dict())
            room = Room().to_dict()
        # room["curr_connections"][session_id] = UserConnection(sid, username).to_dict()
        # room["all_connections"][session_id] = UserConnection(sid, username).to_dict()
        if (session_id not in room["curr_connections"]): room["curr_connections"].append(session_id)
        if (session_id not in room["all_connections"]): room["all_connections"].append(session_id)
        print(room_ref.get().to_dict())
        room_ref.update({"curr_connections": room["curr_connections"], "all_connections": room["all_connections"]})
    
    def leave_room(self, room_id: str, session_id: str, delete_sessions: Callable[[str], None]):
        print(f"{session_id} left the room")
        room_ref = self.rooms.document(room_id)
        room = room_ref.get().to_dict()
        if room:
            # room["curr_connections"].pop(session_id, None)
            try:
                room["curr_connections"].remove(session_id)
            except ValueError:
                pass
            if not room["curr_connections"]:
                # TODO: delete all sessions
                delete_sessions(room_id)
                room_ref.delete()
            else:
                room_ref.update({"curr_connections": room["curr_connections"]})
    
    def get_room_by_id(self, room_id: str) -> dict:
        room_ref = self.rooms.document(room_id)
        room = room_ref.get().to_dict()
        return room

    def get_rooms(self) -> dict:
        return {doc.id: doc.to_dict() for doc in self.rooms.stream()}

    def is_valid_room(self, room_id: str) -> bool:
        rooms = self.get_rooms()
        return room_id in rooms