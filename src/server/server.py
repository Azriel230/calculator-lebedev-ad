from contextlib import asynccontextmanager
import datetime
import json
from fastapi import FastAPI
from pydantic import BaseModel

import database

from database import HistoryInstance
from calculator import handle_calculate_errors
from logger import LOGGER
from tcpserver import TCPServer

HISTORY_SERVER = TCPServer()
logger = LOGGER

@asynccontextmanager
async def lifespan(app: FastAPI):
    HISTORY_SERVER.run()
    yield
    HISTORY_SERVER.stop()


app = FastAPI(lifespan=lifespan)


class CalcBody(BaseModel):
    expression: str

@app.get("/")
async def get_root():
    return


@app.post("/calc")
async def post_calc_handler(body: CalcBody, float: str | None = None):
    res = handle_calculate_errors(body.expression, float)
    h = HistoryInstance(
            timestamp=int(datetime.datetime.now().timestamp()),
            expression=body.expression,
            result=str(res),
        )
    database.insert_history(h)
    HISTORY_SERVER.send_message(json.dumps(h))
    return {"result": res}


@app.get("/history")
async def get_history():
    history = database.select_history()
    return history
