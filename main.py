from fastapi import FastAPI
from contextlib import asynccontextmanager
import secrets

from db.database import (engine, Base)
from models.postgres_models import (Developers)
from routers.developer_router import router as developer_router
from core.redis_client import redis_client


async def create_all_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@asynccontextmanager
async def lifecycle(app:FastAPI):
    
    print("System started...")
    print("Pinging redis...")
    try:
        await redis_client.ping()
        print("Connected to Redis...")
    except Exception as e:
        print(f"Failed to connect to Redis. : {e}")
        raise

    yield

    print("Closing redis...")
    await redis_client.close()
    print("Closing systems...")
    await engine.dispose()



app = FastAPI(title="Auth System", lifespan=lifecycle)
app.include_router(developer_router)


@app.get("/")
def root():
    return {"message":"Auth system is runnning"}


