import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()


def get_engine():
    host = os.getenv("HOST_POSTGRES_HOST", "localhost")
    port = os.getenv("HOST_POSTGRES_PORT", "5432")
    db = os.getenv("HOST_POSTGRES_DB", "worldcup2026")
    user = os.getenv("HOST_POSTGRES_USER", "postgres")
    password = os.getenv("HOST_POSTGRES_PASSWORD", "")

    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
    return create_engine(url)