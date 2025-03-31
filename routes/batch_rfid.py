from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
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
        INSERT INTO batch_rfid_map (customer_id, store_id, batch_id, rfid)
        VALUES (:customer_id, :store_id, :batch_id, :rfid)
    """
    values = link.dict()
    # Fjernet timestamp midlertidig hvis kolonnen ikke finnes
    try:
        await database.execute(query=query, values=values)
        return {"status": "linked", "rfid": link.rfid, "batch_id": link.batch_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RFID link feilet: {str(e)}")


# Modell for RFID-flytting
class RFIDMovement(BaseModel):
    customer_id: str
    store_id: str
    rfid: str
    zone: str

@router.post("/move")
async def move_rfid(movement: RFIDMovement):
    # Hent batch_id basert på aktiv kobling i batch_rfid_map
    fetch_batch_query = """
        SELECT batch_id FROM batch_rfid_map
        WHERE customer_id = :customer_id AND store_id = :store_id AND rfid = :rfid
        ORDER BY id DESC LIMIT 1
    """
    fetch_values = {
        "customer_id": movement.customer_id,
        "store_id": movement.store_id,
        "rfid": movement.rfid
    }
    result = await database.fetch_one(query=fetch_batch_query, values=fetch_values)

    if not result:
        raise HTTPException(status_code=404, detail="RFID ikke funnet eller ikke koblet til en batch")

    batch_id = result["batch_id"]

    # Sjekk siste registrerte sone for denne RFID
    fetch_last_zone_query = """
        SELECT zone FROM rfid_movements
        WHERE customer_id = :customer_id AND store_id = :store_id AND rfid = :rfid
        ORDER BY id DESC LIMIT 1
    """
    last_zone = await database.fetch_one(query=fetch_last_zone_query, values=fetch_values)

    if last_zone and last_zone["zone"] == movement.zone:
        return {
            "status": "skipped",
            "message": f"RFID {movement.rfid} er allerede i sone '{movement.zone}'"
        }

    insert_query = """
        INSERT INTO rfid_movements (customer_id, store_id, batch_id, rfid, zone)
        VALUES (:customer_id, :store_id, :batch_id, :rfid, :zone)
    """
    insert_values = {
        "customer_id": movement.customer_id,
        "store_id": movement.store_id,
        "batch_id": batch_id,
        "rfid": movement.rfid,
        "zone": movement.zone,
    }

    try:
        await database.execute(query=insert_query, values=insert_values)
        return {
            "status": "moved",
            "rfid": movement.rfid,
            "batch_id": batch_id,
            "zone": movement.zone,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Flytting feilet: {str(e)}")
