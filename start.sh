source ../venv/bin/activate
uvicorn main:app --host 0.0.0.0 --ssl-keyfile=../config/privkey.pem --ssl-certfile=../config/fullchain.pem --port 8000