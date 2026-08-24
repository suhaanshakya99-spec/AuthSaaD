from db.database import (LocalSession, engine)

async def get_session():
    async with LocalSession() as session:
        yield session