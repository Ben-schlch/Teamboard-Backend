from services.users import register_user, UserBody, Credentials
from services.connectionmanager import ConnectionManager, verify_token, generate_token
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
import logging
import services.boardedit as boardedit
import json

logging.basicConfig(level=logging.INFO)

app = FastAPI()


async def parse_message(websocket: WebSocket, data: dict, email: str):

    kind_of_object = data["kind_of_object"]
    type_of_edit = data["type_of_edit"]
    boardid = data["teamboard"]["id"] or data["teamboard_id"]
    combined = kind_of_object + type_of_edit
    logging.info(combined)
    try:
        if await boardedit.is_teamboardeditor(boardid, email):
            match combined:  # [teamboard, task, column, subtask]+[edit,create,delete,(move, load)]
                case "boardload":
                    await boardedit.teamboardload(email)
                case "boardadd":
                    await boardedit.teamboardcreate(data, email)
                case "boarddelete":
                    await boardedit.teamboarddelete(data, manager)
                case "boardedit":
                    await boardedit.teamboardedit(data)
                case "taskdelete":
                    await boardedit.taskdelete(data)
                case "taskadd":
                    await boardedit.taskcreate(data)
                case "taskedit":
                    await boardedit.taskedit(data)
                case "statedelete":
                    await boardedit.columndelete(data)
                case "stateadd":
                    await boardedit.columncreate(data)
                case "stateedit":
                    await boardedit.columnedit(data)
                case "subtaskadd":
                    await boardedit.subtaskcreate(data)
                case "subtaskedit":
                    await boardedit.subtaskedit(data)
                case "subtaskdelete":
                    await boardedit.subtaskdelete(data)
                case "subtaskmove":
                    await boardedit.subtaskmove(data)
                case "statemove":
                    await boardedit.columnmove(data)
                case _:
                    raise HTTPException(status_code=404, detail=f"404 {kind_of_object} {type_of_edit}")
        else:
            match combined:  # [teamboard, task, column, subtask]+[edit,create,delete,(move, load)]
                case "boardload":
                    await boardedit.teamboardload(email)
                case "boardadd":
                    await boardedit.teamboardcreate(data, email)
                case _:
                    raise HTTPException(status_code=404, detail=f"404 No editor: {kind_of_object} {type_of_edit} unauthorized")
    except Exception as e:
        await manager.send_personal_message(f"400 {kind_of_object} {type_of_edit}", websocket)
        logging.error(type(e), e)
    else:
        await manager.send_personal_message(f"200 {kind_of_object} {type_of_edit}", websocket)
        jsoned = json.dumps(data)
        boardid = data["teamboard"]["id"] or data["teamboard_id"]
        await manager.broadcast(teamboard=boardid, message=jsoned)


manager = ConnectionManager()


# Define a WebSocket endpoint that requires JWT token authentication
@app.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    try:
        email = verify_token(token)
    except:
        await websocket.close()
    else:
        # Handle WebSocket connection
        await manager.connect(websocket, email)
        logging.info(f"Client #{email} connected")
        await websocket.send_text(f"200")
        try:
            while True:
                data = await websocket.receive_text()
                logging.info(f"Client #{email} sent: {data}")
                try:
                    data = json.loads(data)
                    await parse_message(websocket, data, email)
                except json.JSONDecodeError as e:
                    logging.info(f"JSON Decode Error {e}")
                    await manager.send_personal_message(f"400 JSONDecodeError", websocket)
                except Exception as e:
                    logging.info(f"400 Error with {websocket}: {str(e)}")
                    await manager.send_personal_message(f"400 Error", websocket)
                # await manager.send_personal_message(f"You wrote: {data}", websocket)
                # await manager.broadcast(f"Client #{email} says: {data}")
        except WebSocketDisconnect:
            manager.disconnect(websocket)
            logging.info(f"Client #{email} disconnected")


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
