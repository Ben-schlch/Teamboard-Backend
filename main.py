from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("websocket fastapi")

app = FastAPI()


async def parse_message(data: dict):
    """Check the message from client"""
    #TODO: JSON Format -->
    return 0


async def send_personal_message(message: str, websocket: WebSocket):
    # FIXME: Function or static method in Connection manager?
    await websocket.send_text(message)


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    # TODO: Put websocket connection on pending
    # TODO: Check first message whether it is authenticated --> Put
    #  websocket into list of authenticated for 15 minutes (database??!)
    #  --> how does authentication work? alwin please explain --> Cookie?

    await manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            await send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{user_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{user_id} left the chat")
