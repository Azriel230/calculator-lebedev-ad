import subprocess

def calculate(expr: str, isFloat):
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
