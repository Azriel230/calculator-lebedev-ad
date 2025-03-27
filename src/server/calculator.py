import subprocess

from fastapi import HTTPException


def calculate(expr: str, isFloat: bool):
    command = ["../../build/app.exe"]
    if isFloat:
        command.append("--float")
    try:
        res = subprocess.run(
            command, input=expr, text=True, capture_output=True, timeout=10
        )
    except TimeoutError:
        raise Exception(2)

    if res.returncode != 0:
        raise Exception(res.returncode)
    try:
        if isFloat:
            return float(res.stdout)
        else:
            return int(res.stdout)
    except ValueError:
        raise Exception(1)


def handle_calculate_errors(expr: str, isFloat) -> str | int | float:
    if isFloat == "true":
        isFloat = True
    else:
        isFloat = False
    try:
        res = calculate(expr, isFloat)
    except Exception as e:
        code = e.args[0] - 256
        match code:
            case -1:
                raise HTTPException(
                    status_code=400, detail="unexpected symbol in input"
                )
            case -2:
                raise HTTPException(status_code=400, detail="missmatched paranteses")
            case -3:
                raise HTTPException(
                    status_code=400,
                    detail="stack corrupted during evaluation: expression is incorrect",
                )
            case -4:
                raise HTTPException(status_code=400, detail="input must not be empty")
            case -5:
                raise HTTPException(
                    status_code=400, detail="null division happened during evaluation"
                )
            case -6:
                raise HTTPException(
                    status_code=400,
                    detail="too many operands, expression is not correct",
                )
            case -7:
                raise HTTPException(
                    status_code=400, detail="wrong order, expression is incorrect"
                )
            case -254:
                raise HTTPException(status_code=400, detail="evaluation took too long")
            case _:
                raise HTTPException(status_code=500, detail="unknown calculator error")
    return res
