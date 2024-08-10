import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
from pathlib import Path

load_dotenv()

cred = credentials.Certificate(os.path.join(Path(__file__).parent, os.getenv("FIREBASE_PATH")))

firebase_admin.initialize_app(cred)

db = firestore.client()