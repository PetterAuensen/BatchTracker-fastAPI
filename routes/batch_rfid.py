from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import database

router = APIRouter()

class BatchRFIDLink(BaseModel):
    customer_id: str
    store_id: str
    batch_id: str
    rfid: str

@router.post("/link")
async def link_rfid(data: BatchRFIDLink):
    query = """
        INSERT INTO batch_rfid_map (customer_id, store_id, batch_id, rfid)
        VALUES (:customer_id, :store_id, :batch_id, :rfid)
        ON CONFLICT (customer_id, store_id, rfid)
        DO UPDATE SET batch_id = EXCLUDED.batch_id;
    """
    try:
        await database.execute(query=query, values=data.dict())
        return {"status": "linked", "rfid": data.rfid, "batch_id": data.batch_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))