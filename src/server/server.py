from logger import LOGGER
from fastapi import FastAPI
from pydantic import BaseModel

from calculator import handle_calculate_errors

logger = LOGGER

app = FastAPI()


class CalcBody(BaseModel):
    expression: str

class HistoryInstance(BaseModel):
    timestamp: int
    expression: str
    result: str

@app.get("/")
async def get_root():
    return


@app.post("/calc")
async def post_calc_handler(body: CalcBody, float: str | None = None):
    res = handle_calculate_errors(body.expression,float)
    return {"result": res}

@app.get("/history")
async def get_history():
    mock_history = [HistoryInstance(timestamp=10239238728, expression="10+20",result="30"),HistoryInstance(timestamp=10239238728-1000,expression="10/20",result="0.5") ]
    return mock_history

