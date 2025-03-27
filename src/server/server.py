import time
from logger import LOGGER
from fastapi import FastAPI
from pydantic import BaseModel

from calculator import calculate

logger = LOGGER

app = FastAPI()


class CalcBody(BaseModel):
    expression: str

class HistoryInstance(BaseModel):
    timestamp: float
    expression: str
    result: str

@app.get("/")
async def get_root():
    return


@app.post("/calc")
async def post_calc_handler(body: CalcBody, float: str | None = None):
    if float == "true":
        isFloat = True
    else:
        isFloat = False
    res = calculate(body.expression, isFloat)
    return {"result": res}

@app.get("/history")
async def get_history():
    mock_history = [HistoryInstance(timestamp=time.time(),expression="10+20",result="30"),HistoryInstance(timestamp=time.time()-1000,expression="10/20",result="0.5") ]
    return mock_history

