import os
from databases import Database

DATABASE_URL = os.getenv("DATABASE_URL")
database = Database(DATABASE_URL)

async def init_db():
    query = """
    CREATE TABLE IF NOT EXISTS batches (
        customer_id TEXT NOT NULL,
        store_id TEXT NOT NULL,
        batch_id TEXT NOT NULL,
        article_id TEXT NOT NULL,
        expiration_date TEXT NOT NULL,
        status TEXT NOT NULL,
        production_method TEXT,
        production_place TEXT,
        supplier TEXT,
        dynamic_fields TEXT,
        PRIMARY KEY (customer_id, store_id, batch_id)
    );

    CREATE TABLE IF NOT EXISTS batch_rfid_map (
        customer_id TEXT NOT NULL,
        rfid TEXT NOT NULL,
        store_id TEXT NOT NULL,
        batch_id TEXT NOT NULL,
        PRIMARY KEY (customer_id, rfid)
    );

    CREATE TABLE IF NOT EXISTS batch_movements (
        id SERIAL PRIMARY KEY,
        customer_id TEXT NOT NULL,
        store_id TEXT NOT NULL,
        batch_id TEXT NOT NULL,
        zone TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    await database.execute(query=query)