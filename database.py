import os
from databases import Database

# Henter databasen fra miljøvariabel
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")

# Oppretter databaseobjekt
database = Database(DATABASE_URL)

# Kjør ved oppstart for å opprette nødvendige tabeller
async def init_db():
    await database.connect()

    # Opprett batches-tabellen
    await database.execute("""
        CREATE TABLE IF NOT EXISTS batches (
            customer_id TEXT NOT NULL,
            store_id TEXT NOT NULL,
            batch_id TEXT NOT NULL,
            article_id TEXT NOT NULL,
            expiration_date DATE,
            status TEXT NOT NULL,
            production_method TEXT,
            production_place TEXT,
            supplier TEXT,
            dynamic_fields JSONB,
            PRIMARY KEY (customer_id, store_id, batch_id)
        );
    """)

    # Opprett batch_rfid_map-tabellen
    await database.execute("""
        CREATE TABLE IF NOT EXISTS batch_rfid_map (
            customer_id TEXT NOT NULL,
            rfid TEXT NOT NULL,
            store_id TEXT NOT NULL,
            batch_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (customer_id, store_id, rfid)
        );
    """)

    # Opprett batch_movements-tabellen
    await database.execute("""
        CREATE TABLE IF NOT EXISTS batch_movements (
            id SERIAL PRIMARY KEY,
            customer_id TEXT NOT NULL,
            store_id TEXT NOT NULL,
            batch_id TEXT NOT NULL,
            rfid TEXT NOT NULL,
            zone TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_current_position BOOLEAN
        );
    """)
