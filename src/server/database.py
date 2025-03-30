from pydantic import BaseModel
from dotenv import load_dotenv
import os
import psycopg2
from fastapi import HTTPException


class HistoryInstance(BaseModel):
    timestamp: int
    expression: str
    result: str


def select_history() -> list[HistoryInstance]:
    try:
        load_dotenv("./.env")
        conn = psycopg2.connect(
            port=os.getenv("DBPORT",8888),
            dbname=os.getenv("DBNAME", "calculator"),
            user=os.getenv("DBUSER", "server"),
            host=os.getenv("DBHOST", "localhost"),
            password=os.getenv("DBPASSWORD"),
        )
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM history")
        all_history = cursor.fetchall()
        cursor.close()
        conn.close()
        result = []
        for h in all_history:
            result.append(HistoryInstance(timestamp=h[0], expression=h[1], result=h[2]))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=e.__str__())


def insert_history(h: HistoryInstance):
    try:
        load_dotenv("./.env")
        conn = psycopg2.connect(
            port=os.getenv("DBPORT",8888),
            dbname=os.getenv("DBNAME", "calculator"),
            user=os.getenv("DBUSER", "server"),
            host=os.getenv("DBHOST", "localhost"),
            password=os.getenv("DBPASSWORD"),
        )
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO history (timeReq,expr,result) VALUES (%s,%s,%s)",
            (h.timestamp, h.expression, h.result),
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=e.__str__())
