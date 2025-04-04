from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from database import database

router = APIRouter()

# Modell for kobling av RFID til batch
class RFIDLink(BaseModel):
    customer_id: str
    store_id: str
    batch_id: str
    rfid: str

@router.post("/link")
async def link_rfid(link: RFIDLink):
    query = """
        INSERT INTO batch_rfid_map (customer_id, store_id, batch_id, rfid, created_at)
        VALUES (:customer_id, :store_id, :batch_id, :rfid, :created_at)
    """
    values = link.dict()
    values["created_at"] = datetime.utcnow()
    try:
        await database.execute(query=query, values=values)
        return {"status": "linked", "rfid": link.rfid, "batch_id": link.batch_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Modell for RFID-flytting
class RFIDMovement(BaseModel):
    customer_id: str
    store_id: str
    rfid: str
    zone: str

@router.post("/move")
async def move_rfid(movement: RFIDMovement):
    fetch_batch_query = """
        SELECT batch_id FROM batch_rfid_map
        WHERE customer_id = :customer_id AND store_id = :store_id AND rfid = :rfid
        ORDER BY created_at DESC LIMIT 1
    """
    fetch_values = {
        "customer_id": movement.customer_id,
        "store_id": movement.store_id,
        "rfid": movement.rfid
    }

    try:
        result = await database.fetch_one(query=fetch_batch_query, values=fetch_values)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Databasefeil ved henting av batch")

    if not result:
        raise HTTPException(status_code=404, detail="RFID ikke funnet eller ikke koblet til en batch")

    batch_id = result["batch_id"]

    fetch_last_zone_query = """
        SELECT zone FROM batch_movements
        WHERE customer_id = :customer_id AND store_id = :store_id AND rfid = :rfid
        ORDER BY timestamp DESC LIMIT 1
    """
    try:
        last_zone = await database.fetch_one(query=fetch_last_zone_query, values=fetch_values)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Databasefeil ved henting av sone")

    if last_zone and last_zone["zone"] == movement.zone:
        return {
            "status": "skipped",
            "message": f"RFID {movement.rfid} er allerede i sone '{movement.zone}'"
        }

    insert_query = """
        INSERT INTO batch_movements (customer_id, store_id, batch_id, rfid, zone, timestamp)
        VALUES (:customer_id, :store_id, :batch_id, :rfid, :zone, :timestamp)
    """
    insert_values = {
        "customer_id": movement.customer_id,
        "store_id": movement.store_id,
        "batch_id": batch_id,
        "rfid": movement.rfid,
        "zone": movement.zone,
        "timestamp": datetime.utcnow()
    }

    try:
        await database.execute(query=insert_query, values=insert_values)
        return {
            "status": "moved",
            "rfid": movement.rfid,
            "batch_id": batch_id,
            "zone": movement.zone,
            "timestamp": insert_values["timestamp"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Databasefeil ved innsending av flytting")

# Modell for å hente alle batcher
class BatchQuery(BaseModel):
    customer_id: str
    store_id: str

@router.post("/batches")
async def get_batches(query: BatchQuery):
    select_query = """
        SELECT * FROM batches
        WHERE customer_id = :customer_id AND store_id = :store_id
    """
    values = query.dict()
    try:
        result = await database.fetch_all(query=select_query, values=values)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail="Databasefeil ved henting av batcher")

# Modell for filtrering av batch movements
class MovementFilter(BaseModel):
    customer_id: str
    store_id: str
    article_id: Optional[str] = None

@router.post("/movements")
async def get_batch_movements(filter: MovementFilter):
    values = {
        "customer_id": filter.customer_id,
        "store_id": filter.store_id,
    }

    article_filter = "AND b.article_id = :article_id" if filter.article_id else ""
    if filter.article_id:
        values["article_id"] = filter.article_id

    query = f"""
        SELECT
            bm.store_id,
            b.article_id,
            bm.batch_id,
            bm.rfid,
            bm.zone,
            bm.timestamp
        FROM batch_movements bm
        JOIN batches b
          ON bm.customer_id = b.customer_id
         AND bm.store_id = b.store_id
         AND bm.batch_id = b.batch_id
        WHERE
            bm.customer_id = :customer_id
            AND bm.store_id = :store_id
            AND b.status IN (1, 8)
            {article_filter}
        ORDER BY
            b.article_id,
            bm.batch_id,
            bm.timestamp DESC
    """

    try:
        rows = await database.fetch_all(query=query, values=values)
        return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Databasefeil: {str(e)}")
