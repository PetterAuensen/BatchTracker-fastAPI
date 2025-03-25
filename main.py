from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from database import database, init_db

app = FastAPI(title="BatchTracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await database.connect()
    await init_db()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/")
def read_root():
    return {"status": "BatchTracker is running"}

from pydantic import BaseModel
from typing import Optional, Dict
from datetime import date

class Batch(BaseModel):
    customer_id: str
    store_id: str
    batch_id: str
    article_id: str
    expiration_date: date
    status: str
    production_method: Optional[str] = None
    production_place: Optional[str] = None
    supplier: Optional[str] = None
    dynamic_fields: Optional[Dict[str, str]] = {}

@app.post("/batch")
async def create_or_update_batch(batch: Batch):
    query = """
        INSERT INTO batches (
            customer_id, store_id, batch_id, article_id,
            expiration_date, status, production_method,
            production_place, supplier, dynamic_fields
        )
        VALUES (
            :customer_id, :store_id, :batch_id, :article_id,
            :expiration_date, :status, :production_method,
            :production_place, :supplier, :dynamic_fields
        )
        ON CONFLICT (customer_id, store_id, batch_id)
        DO UPDATE SET
            article_id = EXCLUDED.article_id,
            expiration_date = EXCLUDED.expiration_date,
            status = EXCLUDED.status,
            production_method = EXCLUDED.production_method,
            production_place = EXCLUDED.production_place,
            supplier = EXCLUDED.supplier,
            dynamic_fields = EXCLUDED.dynamic_fields;
    """
    values = batch.dict()
    await database.execute(query=query, values=values)
    return {"status": "created", "batch_id": batch.batch_id}