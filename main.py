from services.users import register_user, UserBody, Credentials
from services.connectionmanager import ConnectionManager, verify_token, generate_token
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI()


async def parse_message(data: dict):
    """Check the message from client"""
    # TODO: JSON Format -->
    return 0

manager = ConnectionManager()


# Define a WebSocket endpoint that requires JWT token authentication
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        token = websocket.headers['token']
        email = verify_token(token)
    except KeyError:
        await websocket.close(code=401, reason="Token missing")
    except HTTPException:
        await websocket.close(code=401, reason="Token value is wrong")
    else:
        # Handle WebSocket connection
        await manager.connect(websocket)
        await websocket.send_text(f"Welcome, {email}!")
        try:
            while True:
                data = await websocket.receive_text()
                await manager.send_personal_message(f"You wrote: {data}", websocket)
                await manager.broadcast(f"Client #{email} says: {data}")
        except WebSocketDisconnect:
            manager.disconnect(websocket)
            await manager.broadcast(f"Client #{email} left the chat")


# Define an HTTP endpoint that generates a JWT token given an email and password
@app.post("/token")
async def get_token(creds: Credentials):
    return {"token": await generate_token(**creds.dict())}


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/register/")
async def register(user: UserBody):
    return await register_user(**user.dict())

# # debug:
# import uvicorn
#
# if __name__ == "__main__":
#     uvicorn.run(app, host="127.0.0.1", port=8000)
