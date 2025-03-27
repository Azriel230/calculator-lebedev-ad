from logger import LOGGER
from fastapi import FastAPI
from pydantic import BaseModel

from calculator import calculate

logger = LOGGER

app = FastAPI()


class CalcBody(BaseModel):
    expression: str


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
