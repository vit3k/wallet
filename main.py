from typing import Union

from fastapi.responses import JSONResponse, Response
from fastapi import FastAPI
import data.stocks
import data.database
import json
import uvicorn

class JSONDirectResponse(Response):
    media_type = "application/json"

db = data.database.get_database("user=postgres password=* host=db.cfwhcubsayehudtvrfxk.supabase.co port=5432 dbname=postgres")

app = FastAPI()


@app.get("/stocks")
async def read_root():
    stocks_data = data.stocks.get_stocks_data(db)
    #stocks_data['transaction_date'] = stocks_data['transaction_date'].astype(str)
    result = stocks_data.to_json(orient='records')
    return JSONDirectResponse(result)

if __name__ == "__main__":
    uvicorn.run("main:app", host='0.0.0.0', port=8000, reload=True)