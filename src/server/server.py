from logger import LOGGER
from fastapi import FastAPI
from pydantic import BaseModel
from database import HistoryInstance
from calculator import handle_calculate_errors
import database

logger = LOGGER

app = FastAPI()


class CalcBody(BaseModel):
    expression: str



@app.get("/")
async def get_root():
    return


@app.post("/calc")
async def post_calc_handler(body: CalcBody, float: str | None = None):
    res = handle_calculate_errors(body.expression,float)
    return {"result": res}

@app.get("/history")
async def get_history():
    history=database.select_history();
    #если впадлу поднимать,то юзайте
    #mock_history = [HistoryInstance(timestamp=10239238728, expression="10+20",result="30"),HistoryInstance(timestamp=10239238728-1000,expression="10/20",result="0.5") ]
    return history

@app.post("/history")
async def post_history(h:HistoryInstance):
    #если впадлу вдвойне, то юзайте
    #print(h)
    database.insert_history(h)
    return




