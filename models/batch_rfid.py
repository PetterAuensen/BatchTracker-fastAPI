from pydantic import BaseModel

class BatchRFIDLink(BaseModel):
    customer_id: str
    store_id: str
    batch_id: str
    rfid: str