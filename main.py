import asyncio
import logging
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FastAPI app")

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


async def heavy_data_processing(data: dict):
    """Some (fake) heavy data processing logic."""
    await asyncio.sleep(2)
    message_processed = data.get("message", "").upper()
    return message_processed


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Accept the connection from a client.
    await websocket.accept()

    while True:
        try:
            # Receive the JSON data sent by a client.
            data = await websocket.receive_json()
            # Some (fake) heavey data processing logic.
            message_processed = await heavy_data_processing(data)
            # Send JSON data to the client.
            await websocket.send_json(
                {
                    "message": message_processed,
                    "time": datetime.now().strftime("%H:%M:%S"),
                }
            )
        except WebSocketDisconnect:
            logger.info("The connection is closed.")
            break