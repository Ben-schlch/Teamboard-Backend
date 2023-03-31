
from services.users import register_user, UserBody, Credentials
from services.connectionmanager import ConnectionManager, verify_token, generate_token
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
import logging
import services.boardedit as boardedit
import json

logging.basicConfig(level=logging.INFO)

app = FastAPI()


async def parse_message(websocket: WebSocket, data: dict, email: str):
    kind_of_object = "ObjectError"
    type_of_edit = "EditError"
    try:
        kind_of_object = data["kind_of_object"]
        type_of_edit = data["type_of_edit"]
        boardid = data["teamboard"]
        if boardedit.is_teamboardeditor(boardid, email):
            match kind_of_object + type_of_edit:  # [teamboard, task, column, subtask]+[edit,create,delete,(move, load)]
                case "teamboardelete:":
                    await boardedit.teamboarddelete(data, email)
                case "teamboardedit:":
                    await boardedit.teamboardedit(data)
                case "taskdelete:":
                    await boardedit.taskdelete()
                case "taskcreate:":
                    await boardedit.taskcreate()
                case "taskedit:":
                    await boardedit.taskedit()
                case "columndelete:":
                    await boardedit.columndelete()
                case "columncreate:":
                    await boardedit.columncreate()
                case "columnedit:":
                    await boardedit.columnedit()
                case "subtaskcreate:":
                    await boardedit.subtaskcreate()
                case "subtaskedit:":
                    await boardedit.subtaskedit()
                case "subtaskdelete:":
                    await boardedit.subtaskdelete()
                case "subtaskmove:":
                    await boardedit.subtaskmove(data)
                case "columnmove:":
                    await boardedit.columnmove(data)
                case _:
                    raise HTTPException(403)
        else:
            match kind_of_object + type_of_edit:  # [teamboard, task, column, subtask]+[edit,create,delete,(move, load)]
                case "teamboardload":
                    await boardedit.teamboardload(email)
                case "teamboardcreate:":
                    await boardedit.teamboardcreate(data, email)
                case _:
                    raise HTTPException(403)
    except Exception:
        print("Exception!")
        await manager.send_personal_message(f"403 {kind_of_object} {type_of_edit}", websocket)

    else:
        await manager.send_personal_message(f"200 {kind_of_object} {type_of_edit}", websocket)
        jsoned = json.dumps(data)
        await manager.broadcast(teamboard=int(data["teamboard"]), message=jsoned)


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
        await manager.connect(websocket, email)
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
