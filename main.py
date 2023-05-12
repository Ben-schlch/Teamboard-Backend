import psycopg

from services.users import register_user, UserBody, Credentials, confirm_token, verify_reset_token, reset_password, \
    check_password_complexity, send_reset_token
from services.connectionmanager import ConnectionManager, verify_token, generate_token
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Response
from fastapi.responses import FileResponse
from fastapi.requests import Request
import logging
import services.boardedit as boardedit
import json

logging.basicConfig(filename="teamboardlog.log",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)

app = FastAPI()


async def parse_message(websocket: WebSocket, data: dict, email: str):
    """
    Parses the message and calls the corresponding function.
    Catches JSON DEcode errors and tries to send a message to the client(s).
    Sends the changes to the needed people.
    Checks if the user is allowed to edit the board.
    :param websocket: WebSocket
    :param data: JSON Message
    :param email: Email of the user who is sending the message
    :return:
    """


    kind_of_object = data["kind_of_object"]
    type_of_edit = data["type_of_edit"]
    boardid = data.get("teamboard", {}).get("id") or data.get("teamboard_id")
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
                case "statemoveSubtaskInState":
                    await boardedit.subtaskmove(data)
                case "statemoveSubtaskBetweenStates":
                    await boardedit.subtaskmove(data)
                case "statemove":
                    await boardedit.columnmove(data)
                case "teamboardaddUser":
                    teamboard = await boardedit.teamboardadduser(data, email)
                    if not teamboard:
                        return
                    try:
                        websocket_added = \
                            [result[0] for result in manager.active_connections if result[1] == data["email"]][0]
                        await manager.send_personal_message(json.dumps(data), websocket_added)
                        # await manager.send_personal_message(f"200 {kind_of_object} {type_of_edit}", websocket)
                    except IndexError:
                        logging.info("User who was added is not online")
                        # await manager.send_personal_message(f"404 {kind_of_object} {type_of_edit}", websocket)
                    return
                case "teamboarddeleteUser":
                    result = await boardedit.teamboarddeleteuser(data)
                    if not result:
                        return
                    if result:
                        try:
                            websocket_deleted = \
                                [result[0] for result in manager.active_connections if result[1] == data["email"]][0]
                            await manager.send_personal_message(json.dumps(data), websocket_deleted)
                            # await manager.send_personal_message(f"200 {kind_of_object} {type_of_edit}", websocket)
                        except IndexError:
                            logging.info("User who was deleted is not online")
                            # await manager.send_personal_message(f"400 with {kind_of_object} {type_of_edit}", websocket)
                        return
                case _:
                    raise HTTPException(status_code=404, detail=f"400 with {kind_of_object} {type_of_edit}")
        else:
            match combined:  # [teamboard, task, column, subtask]+[edit,create,delete,(move, load)]
                case "boardload":
                    jason = json.dumps(await boardedit.teamboardload(email))
                    await manager.send_personal_message(jason, websocket)  # temporary workaround
                    return
                case "boardadd":
                    await boardedit.teamboardcreate(data, email)
                case _:
                    raise HTTPException(status_code=404,
                                        detail=f"404 No editor: {kind_of_object} {type_of_edit} unauthorized")
    except HTTPException as e:
        # await manager.send_personal_message(f"400 HTTPExceptiom {kind_of_object} {type_of_edit}", websocket)
        logging.error(type(e), e)
    except psycopg.Error as e:
        # await manager.send_personal_message(f"400 psycopg.Error {kind_of_object} {type_of_edit}", websocket)
        logging.error(type(e), e)
    except Exception as e:
        # await manager.send_personal_message(f"400 {kind_of_object} {type_of_edit}", websocket)
        logging.error(type(e), e)
    else:
        # await manager.send_personal_message(f"200 {kind_of_object} {type_of_edit}", websocket)
        jsoned = json.dumps(data)
        boardid = data.get("teamboard", {}).get("id") or data.get("teamboard_id")
        await manager.broadcast(teamboard=boardid, message=jsoned)


manager = ConnectionManager()


# Define a WebSocket endpoint that requires JWT token authentication
@app.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str, response: Response):
    """
    Handles the websocket connection.
    Communication of all edits/loads/...
    Authentication by using a JWT token acqquired by the login endpoint
    :param websocket: websocket
    :param token: JWT Token str from login endpoint
    :param response:
    :return:
    """
    try:
        email = verify_token(token)
    except Exception:
        await websocket.close()
    else:
        # Handle WebSocket connection
        await manager.connect(websocket, email)
        logging.info(f"Client #{email} connected")
        # await websocket.send_text(f"200")
        try:
            while True:
                data = await websocket.receive_text()
                logging.info(f"Client #{email} sent: {data}")
                try:
                    data = json.loads(data)
                    await parse_message(websocket, data, email)
                except json.JSONDecodeError as e:
                    logging.info(f"JSON Decode Error {e}")
                    # await manager.send_personal_message(f"400 JSONDecodeError", websocket)
                except Exception as e:
                    logging.info(f"400 Error with {websocket}: {type(e)}: {str(e)}")
                    # await manager.send_personal_message(f"400 Error Parsemessage", websocket)
                # await manager.send_personal_message(f"You wrote: {data}", websocket)
                # await manager.broadcast(f"Client #{email} says: {data}")
        except WebSocketDisconnect:
            manager.disconnect(websocket)
            logging.info(f"Client #{email} disconnected")


# Define an HTTP endpoint that generates a JWT token given an email and password
@app.post("/login")
async def get_token(creds: Credentials, response: Response):
    """
    Endpoint for logging in --> returns a JWT token with 30 min validity
    :param creds: Credentials (pwd and email)
    :param response:
    :return:
    """
    logging.info(f"Trying logging in user {creds.email}")
    try:
        return {"token": await generate_token(**creds.dict())}
    except HTTPException as e:
        response.status_code = e.status_code
        return {"detail": e.detail}


@app.post("/register/")
async def register(user: UserBody, response: Response):
    """
    Registers the user and sends a confirmation email which needs to be confirmed before login
    :param user:
    :param response:
    :return:
    """
    if not await check_password_complexity(user.pwd):
        response.status_code = 406
        return {"detail": "Password not complex enough"}
    logging.info(f"Trying registering user {user.email}")
    try:
        return await register_user(**user.dict())
    except HTTPException as e:
        response.status =  e.status_code


@app.get("/confirm/{token}")
async def confirm(token: str, response: Response):
    """
    Confirms the email address of the user
    :param token:
    :param response:
    :return:
    """
    if await confirm_token(token):
        return FileResponse('html/confirm_mail.html')

    else:
        response.status_code = 401
        return FileResponse('html/confirm_email_wrong.html')


@app.get("/send_reset_mail/{email}")
async def send_reset(email: str, response: Response):
    """
    Sends a reset email to the user
    :param email:
    :param response:
    :return:
    """
    if email == "":
        response.status_code = 401
        return
    elif email:
        await send_reset_token(email)
    else:
        response.status_code = 401
        return


@app.get("/reset/{token}")
async def reset_page(response: Response):
    """
    Reset the password of the user
    :param response:
    :return:
    """
    return FileResponse('html/reset.html')


@app.post("/reset")
async def reset_pwd(request: Request, response: Response):
    body = await request.json()
    token = body["token"]
    password = body["password"]
    email = body["email"]
    if await verify_reset_token(email, token):
        if await check_password_complexity(password):
            await reset_password(email, password)
            return
        else:
            return Response(status_code=406, content="Sorry but your password is not complex enough. "
                                                     "It needs to be at least 8 characters long and contain "
                                                     "at least one number, one lower character and one upper character.")
    else:
        return Response(status_code=406, content="Sorry but something went wrong. "
                                                 "The link you clicked might be outdated.")
