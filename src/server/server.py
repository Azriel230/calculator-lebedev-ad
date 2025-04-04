from contextlib import asynccontextmanager
import datetime
import json
from fastapi import FastAPI,Response,Request
from pydantic import BaseModel

import database
import structlog
import os
from dotenv import load_dotenv
from starlette.concurrency import iterate_in_threadpool

from database import HistoryInstance
from calculator import handle_calculate_errors
from logger import LOGGER
from tcpserver import TCPServer

HISTORY_SERVER = TCPServer()
logger = LOGGER

load_dotenv("./.env")

@asynccontextmanager
async def lifespan(app: FastAPI):
    HISTORY_SERVER.run()
    LOGGER.info("HTTP: Server started",port=os.getenv("HTTPSERVERPORT",8080),host=os.getenv("HTTPSERVERHOST","localhost"))
    yield
    HISTORY_SERVER.stop()
    LOGGER.info("HTTP: Server stoped")




app = FastAPI(lifespan=lifespan)

@app.middleware("http")
async def logger_middleware(request:Request, call_next):
    structlog.contextvars.clear_contextvars()

    structlog.contextvars.bind_contextvars(
        path=request.url.path,
        method=request.method,
        client_host=request.client.host,
    )

    response = await call_next(request)
    response_body = [chunk async for chunk in response.body_iterator]
    response.body_iterator = iterate_in_threadpool(iter(response_body))   
    body=json.loads((b''.join(response_body)).decode())
    structlog.contextvars.bind_contextvars(
        status_code=response.status_code,
    )

    if 400 <= response.status_code < 500:
        logger.warn("HTTP: Client error",detail=body.get("detail"))
    elif response.status_code >= 500:
        logger.error("HTTP: Server error",detail=body.get("detail"))
    else:
        logger.info("HTTP: OK")


    return response


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
    HISTORY_SERVER.send_message(
        json.dumps(
            {
                "timestamp": h.timestamp,
                "expression": h.expression,
                "result": h.result,
            }
        )
    )
    return {"result": res}


@app.get("/history")
async def get_history():
    history = database.select_history()
    return history
