import logging
import random
import queue

from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import asyncio
import time
import threading

from pocket_options_consumer import exchange_rate_pocket_options_consumer

app = FastAPI()

exchange_rate_queue = queue.Queue()


# Set up own logging (separated from uvicorn)
logging.basicConfig(level=logging.INFO)  # Set the logging level
logger = logging.getLogger(__name__)  # Use module-level logger

# Allow CORS for Vue.js frontend1
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:9000"],  # Replace with your Vue.js URL
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


app = FastAPI()


# app.mount("/static", StaticFiles(directory="static"), name="static")


async def dashboard_frontend_propagation(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            await websocket.send_json({"time": time.strftime("%Y-%m-%d %H:%M:%S")})
            await asyncio.sleep(1)
        except WebSocketDisconnect:
            break


async def exchange_rate_frontend_propagation(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            # Replace this with actual exchange rate fetching logic
            exchange_rate = {
                "assetName": "BTC",
                "exchangeRate": random.uniform(0.5, 1.2),
                "timestamp": datetime.now().isoformat()
            }
            logger.info("Propagating exchange rates:")
            await websocket.send_json(exchange_rate)
            await asyncio.sleep(5)
        except WebSocketDisconnect:
            break


@app.websocket("/ws/dashboard")
async def dashboard_endpoint(websocket: WebSocket):
    await dashboard_frontend_propagation(websocket)


@app.websocket("/ws/exchangerates")
async def exchange_rate_endpoint(websocket: WebSocket):
    await exchange_rate_frontend_propagation(websocket)


@app.post("/update_user_name")
async def update_user_name(user_name_update: UserNameUpdate):
    global user_name
    user_name = user_name_update.new_name
    logger.info(f"User name updated to {user_name}")
    return {"message": "User name updated successfully"}


# @app.get("/")
# async def root():
#    with open("index.html") as f:
#        return HTMLResponse(content=f.read())


# Run in separate threads for concurrency
exchange_rate_consumer_thread = threading.Thread(target=asyncio.run, args=(exchange_rate_pocket_options_consumer(exchange_rate_queue),))

if __name__ == "__main__":
    logger.info("Starting backend threads.. ")
    exchange_rate_consumer_thread.start()
    logger.info("All backend threads initialized..")

    import uvicorn

    logger.info("Starting uvicorn fast api backend.. ")
    uvicorn.run(app, host="0.0.0.0", port=8001)
