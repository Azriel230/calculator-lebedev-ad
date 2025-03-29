from pydantic import BaseModel
from dotenv import load_dotenv
import os
import psycopg2
import datetime
from fastapi import HTTPException


class HistoryInstance(BaseModel):
    timestamp: int
    expression: str
    result: str


def select_history()->list[HistoryInstance]:
    try:
        conn=psycopg2.connect(dbname='calculator', user='server',host=os.getenv('DBHOST', "localhost"))
        cursor=conn.cursor()
        cursor.execute('SELECT * FROM history')
        all_history=cursor.fetchall()
        cursor.close()
        conn.close()
        result=[]
        for h in all_history:
            result.append(HistoryInstance(timestamp=h[0],expression=h[1],result=h[2]))
        return result
    except Exception as e:
        raise HTTPException(status_code=500,detail=e.__str__())


def insert_history(h:HistoryInstance):
    try:
        conn=psycopg2.connect(dbname='calculator', user='server',host=os.getenv('DBHOST', "localhost"))
        cursor=conn.cursor()
        cursor.execute('INSERT INTO history (timeReq,expr,result) VALUES (%s,%s,%s)', (h.timestamp,h.expression,h.result))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        raise HTTPException(status_code=500,detail=e.__str__())







