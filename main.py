from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import date
import json

from database import database, init_db
from routes import batch_rfid  # ✅ Sørger for at hele modulen er tilgjengelig

app = FastAPI(title="BatchTracker API")

# Aktiver CORS slik at frontend får tilgang til API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # I prod bør du sette eksakt domene her
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Inkluder alle ruter fra batch_rfid.py, med felles prefix /rfid
app.include_router(batch_rfid.router, prefix="/rfid", tags=["Batch RFID"])

# Koble til database ved oppstart
@app.on_event("startup")
async def startup():
    await database.connect()
    await init_db()

# Koble fra database ved nedstengning
@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Helse-endepunkt
@app.get("/")
def read_root():
    return {"status": "BatchTracker is running"}

# Datamodell for batch
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

# Endepunkt for å opprette eller oppdatere batch
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
    values["dynamic_fields"] = json.dumps(values["dynamic_fields"])
    try:
        await database.execute(query=query, values=values)
        return {"status": "created", "batch_id": batch.batch_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
