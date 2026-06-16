from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import time
from sqlalchemy import MetaData
shared_metadata = MetaData()

load_dotenv()

DATABASE_URL = (
        f"mysql+pymysql://{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}"
        f"@{os.environ['DB_HOST']}/{os.environ['DB_NAME']}"
    )

MAX_RETRIES = 15
RETRY_DELAY = 5

engine = None

for attempt in range(MAX_RETRIES):

    try:
        engine = create_engine(DATABASE_URL)

        connection = engine.connect()
        connection.close()

        print("Database connection established.")
        break

    except Exception as e:

        print(f"[DB WAIT] Attempt {attempt+1}/{MAX_RETRIES}")
        print(str(e))

        time.sleep(RETRY_DELAY)

if engine is None:
    raise Exception("Could not connect to database.")

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)