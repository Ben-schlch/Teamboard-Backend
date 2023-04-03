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
                case "teamboardload":
                    await boardedit.teamboardload(email)
                case "teamboardcreate:":
                    await boardedit.teamboardcreate(data, email)
                case "teamboardelete:":
                    await boardedit.teamboarddelete(data)
                case "teamboardedit:":
                    await boardedit.teamboardedit(data)
                case "taskdelete:":
                    await boardedit.taskdelete(data)
                case "taskcreate:":
                    await boardedit.taskcreate(data)
                case "taskedit:":
                    await boardedit.taskedit(data)
                case "columndelete:":
                    await boardedit.columndelete(data)
                case "columncreate:":
                    await boardedit.columncreate(data)
                case "columnedit:":
                    await boardedit.columnedit(data)
                case "subtaskcreate:":
                    await boardedit.subtaskcreate(data)
                case "subtaskedit:":
                    await boardedit.subtaskedit(data)
                case "subtaskdelete:":
                    await boardedit.subtaskdelete(data)
                case "subtaskmove:":
                    await boardedit.subtaskmove(data)
                case "columnmove:":
                    await boardedit.columnmove(data)
                case _:
                    await manager.send_personal_message(f"400 {kind_of_object} {type_of_edit}", websocket)
        else:
            match kind_of_object + type_of_edit:  # [teamboard, task, column, subtask]+[edit,create,delete,(move, load)]
                case "teamboardload":
                    await boardedit.teamboardload(email)
                case "teamboardcreate:":
                    await boardedit.teamboardcreate(data, email)
                case _:
                    await manager.send_personal_message(f"400 {kind_of_object} {type_of_edit}", websocket)
    except Exception as e:
        logging.warning(e)
        await manager.send_personal_message(f"500 {kind_of_object} {type_of_edit}", websocket)
    else:
        await manager.send_personal_message(f"200 {kind_of_object} {type_of_edit}", websocket)
        jsoned = json.dumps(data)
        await manager.broadcast(teamboard=int(data["teamboard"]), message=jsoned)


manager = ConnectionManager()


# Define a WebSocket endpoint that requires JWT token authentication
@app.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    try:
        email = verify_token(token)
    except KeyError:
        await websocket.close(code=401, reason="Token missing")
    except HTTPException:
        await websocket.close(code=401, reason="Token value is wrong")
    else:
        # Handle WebSocket connection
        await manager.connect(websocket, email)
        logging.debug(f"Client #{email} connected")
        await websocket.send_text(f"200")
        try:
            while True:
                data = await websocket.receive_text()
                logging.info(f"Client #{email} sent: {data}")

                await parse_message(websocket, json.loads(data), email)
                # await manager.send_personal_message(f"You wrote: {data}", websocket)
                # await manager.broadcast(f"Client #{email} says: {data}")
        except WebSocketDisconnect:
            manager.disconnect(websocket)
            logging.debug(f"Client #{email} disconnected")


# Define an HTTP endpoint that generates a JWT token given an email and password
@app.post("/login")
async def get_token(creds: Credentials):
    logging.info(f"Trying logging in user {creds.email}")
    return {"token": await generate_token(**creds.dict())}


@app.get("/authenticate/{token}")
async def authenticate():
    return {"message": "Hello World"}


@app.post("/register/")
async def register(user: UserBody):
    logging.info(f"Trying registering user {user.email}")
    return await register_user(**user.dict())

# # debug:
# import uvicorn
#
# if __name__ == "__main__":
#     uvicorn.run(app, host="127.0.0.1", port=8000)
