import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import asyncio

app = FastAPI()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Allow CORS for Vue.js frontend1
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Replace with your Vue.js URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
start_time = datetime.now()
user_name = "Default User"


# Define the request body using Pydantic model
class UserNameUpdate(BaseModel):
    new_name: str  # This should match the expected field name


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except WebSocketDisconnect:
                self.disconnect(connection)


manager = ConnectionManager()


@app.websocket("/ws/realtime")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Broadcast real-time data every second
            current_time = datetime.now()
            uptime = current_time - start_time
            message = {
                "current_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "uptime": str(uptime).split(".")[0],  # Uptime in HH:MM:SS
                "user_name": user_name,
            }
            await manager.broadcast(message)
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.post("/update_user_name")
async def update_user_name(user_name_update: UserNameUpdate):
    global user_name
    user_name = user_name_update.new_name
    logger.info(f"User name updated to {user_name}")
    return {"message": "User name updated successfully"}
