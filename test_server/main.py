import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Create a Socket.IO server with CORS support
sio = socketio.AsyncServer(cors_allowed_origins=[], async_mode="asgi")

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware to FastAPI app
origins = [
    "http://localhost:4200",  # Add your frontend URL here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Socket.IO app to FastAPI
app.mount("/socket.io", socketio.ASGIApp(sio))

# Define your Socket.IO event handlers
@sio.event
async def connect(sid, environ):
    print("connect ", sid)

@sio.event
async def disconnect(sid):
    print("disconnect ", sid)



# Define your FastAPI routes
@app.get("/")
def read_root():
    return {"Hello": "World"}

if __name__ == "__main__":
    uvicorn.run(app, host = "localhost", port = 8000, log_level='debug', access_log=True)