from firebase_init import db
from firebase_admin import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from uuid import uuid4

class SessionManager:
    '''
        Session Manager

        Connects to the firebase db and adds/removes session from rooms
    '''
    def __init__(self):
        self.sessions = db.collection('Sessions')

    def generate_session_id(self):
        while True:
            session_id = str(uuid4())
            if not self.get_session_id_exists(session_id):
                return session_id

    def get_session_id_exists(self, session_id: str) -> bool:
        session_ref = self.sessions.document(session_id)
        return session_ref.get().exists
    
    def get_session(self, session_id: str) -> dict:
        session_ref = self.sessions.document(session_id)
        session = session_ref.get().to_dict()
        return session

    def create_session(self, room_id: str, username: str) -> str:
        session_id = self.generate_session_id()
        self.sessions.document(session_id).set({
            "curr_sid": None,
            "room_id": room_id,
            "username": username,
            "timestamp": firestore.SERVER_TIMESTAMP,
            "socket_timestamp": None
        })
        return session_id

    def update_session(self, session_id: str, sid: str):
        session_ref = self.sessions.document(session_id)
        session_ref.update({"curr_sid": sid, "socket_timestamp": firestore.SERVER_TIMESTAMP})

    def get_room_by_sid(self, sid: str) -> dict:
        for result in self.sessions.where(filter=FieldFilter("curr_sid", "==", sid)).stream():
            room = result.to_dict()
            room["session_id"] = result.id
            return room

    def get_username(self, session_id: str) -> str:
        session_ref = self.sessions.document(session_id)
        return session_ref.get().get("username")
    
    def get_usernames(self, session_ids: list) -> list[str]:
        session_refs = [self.sessions.document(session_id) for session_id in session_ids]
        docs = db.get_all(session_refs)
        return [doc.to_dict().get("username") for doc in docs if doc.exists]
        # return [self.sessions.document(session_id).get().to_dict().get("username") for session_id in session_ids]

    # delete session when room it belongs to is deleted, when user leaves the room
    def delete_session(self, session_id: str):
        session_ref = self.sessions.document(session_id)
        session_snapshot = session_ref.get()
        if session_snapshot.exists:
            session_ref.delete()

    def delete_session_by_room_id(self, room_id: str):
        for result in self.sessions.where(filter=FieldFilter("room_id", "==", room_id)).stream():
            if result.exists:
                result.reference.delete()