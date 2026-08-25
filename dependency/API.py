from fastapi.security import APIKeyHeader 
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException
from sqlalchemy import select
from core.redis_client import redis_client
from dependency.db import get_session
from core.auth import get_developer_Byemail
from models.postgres_models import (Developers, Projects)

api_key_header = APIKeyHeader(name="API key")

async def verify_api_key(db:AsyncSession, developer:Developers, api_key:str=Depends(api_key_header)):

    cached_api_key = redis_client.get(api_key)

    if cached_api_key:
        return {"message":"Verified API"}
    
    stmt = select(Projects).where(Projects.developer_id == developer.id)
    result = await db.execute(stmt)
    developer_projects = result.scalars().all()

    for project in developer_projects:
        if api_key == project.api:
            return {"message":"Verified API"}


    raise HTTPException(status_code=401, detail="API key is not valid")

    

    