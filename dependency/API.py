from fastapi.security import APIKeyHeader 
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException
from sqlalchemy import select
from core.redis_client import redis_client
from dependency.db import get_session
from core.auth import get_developer_Byemail
from models.postgres_models import (Developers, Projects)
import json

api_key_header = APIKeyHeader(name="API-key", auto_error=True)

async def verify_api_key(db:AsyncSession, api_key:str=Depends(api_key_header))->dict:

    cached_api_key = await redis_client.get(api_key)

    if cached_api_key:
        return json.loads(cached_api_key)
    
    stmt = select(Projects).where(Projects.api == api_key)
    result = await db.execute(stmt)
    developer_project = result.scalar_one_or_none()

    if developer_project:
        result = {"project_id":developer_project.id,
                    "developer_id":developer_project.developer_id,
                    "API":developer_project.api}
        await redis_client.set(name=api_key, value=json.dumps(result), ex=300)
        return result
    

    raise HTTPException(status_code=401, detail="API key is not valid")

    

    