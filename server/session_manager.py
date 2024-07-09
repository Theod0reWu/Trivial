from firebase_init import db
from firebase_admin import firestore
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

    def create_session(self, room_id: str) -> str:
        session_id = self.generate_session_id()
        self.sessions.document(session_id).set({
            "room_id": room_id,
            "timestamp": firestore.SERVER_TIMESTAMP
        })
        return session_id

    def get_room_id(self, session_id):
        return self.sessions.document(session_id).get().to_dict()["room_id"]

    # delete session when room it belongs to is deleted, when user leaves the room
    def delete_session(self, session_id: str):
        session_ref = self.sessions.document(session_id)
        session_ref.delete()