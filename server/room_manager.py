from firebase_init import db
from firebase_admin import firestore

class UserConnection:
    def __init__(self, sid: str, username: str):
        self.curr_sid = sid # socket.io session id
        self.username = username
        self.timestamp = firestore.SERVER_TIMESTAMP
    
    @staticmethod
    def from_dict(source):
        conn = UserConnection(**source)
        return conn

    def to_dict(self):
        return {
            "curr_sid": self.curr_sid,
            "username": self.username
        }

    def __repr__(self):
        return f"UserConnection(\
                curr_sid={self.curr_sid}, \
                username={self.username}\
            )"

class Room:
    def __init__(self, state: str = "pregame", curr_connections: dict[str, dict[str, str]] = None, 
                 all_connections: dict[str, dict[str, str]] = None):
        self.state = state
        self.curr_connections = curr_connections if curr_connections is not None else {}
        self.all_connections = all_connections if all_connections is not None else {} # session_id: {sid, username, timestamp_connected}
    
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
                curr_connections={", ".join([session_id+": "+str(conn) for session_id, conn in self.curr_connections.items()])}, \
                all_connections={", ".join([session_id+": "+str(conn) for session_id, conn in self.all_connections.items()])}\
            )"

class RoomManager:
    def __init__(self):
        self.rooms = db.collection('Rooms')
    
    def create_room(self, room_id: str):
        room_ref = self.rooms.document(room_id)
        room = Room()
        print("room creation", room)
        room_ref.set(room.to_dict())

    def join_room(self, room_id: str, session_id: str, sid: str, username: str):
        room_ref = self.rooms.document(room_id)
        room = room_ref.get().to_dict()
        print("room debugging!!!", room, room_id)
        if not room:
            self.create_room(room_id)
            print("new room", room_ref.get().to_dict())
            room = Room().to_dict()
        room["curr_connections"][session_id] = UserConnection(sid, username).to_dict()
        room["all_connections"][session_id] = UserConnection(sid, username).to_dict()
        print(room_ref.get().to_dict())
        room_ref.update({"curr_connections": room["curr_connections"], "all_connections": room["all_connections"]})
    
    def leave_room(self, room_id: str, session_id: str):
        room_ref = self.rooms.document(room_id)
        room = room_ref.get().to_dict()
        if room:
            room["curr_connections"].pop(session_id, None)
            if not room["curr_connections"]:
                # TODO: delete all sessions
                room_ref.delete()
            else:
                room_ref.update({"curr_connections": room["curr_connections"]})
    
    def get_room(self, room_id):
        room_ref = self.rooms.document(room_id)
        room = room_ref.get().to_dict()
        return room

    def get_rooms(self):
        return {doc.id: doc.to_dict() for doc in self.rooms.stream()}