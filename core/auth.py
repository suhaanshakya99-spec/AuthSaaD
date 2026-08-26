import jwt
import pwdlib
from models.postgres_models import (Developers)
from sqlalchemy import (select)
from core.config import settings
from fastapi.security import OAuth2PasswordBearer
from datetime import (datetime, timedelta)
from fastapi import (Depends, HTTPException)
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import APIKeyHeader
import json
from dependency.db import get_session
from core.redis_client import (redis_client)

password_util = pwdlib.PasswordHash.recommended()

def hash_password(plain_password:str):
    hashed_password = password_util.hash(plain_password)
    return hashed_password


def create_access_token(payload:dict):

    expire_time = datetime.now() + timedelta(minutes=settings.ACESS_TOKEN_EXPIRE)

    to_encode = payload.copy()
    to_encode.update({"exp":expire_time})

    access_token = jwt.encode(payload=to_encode, key=settings.KEY, algorithm=settings.ALGORITHM)

    return access_token

def create_refresh_token(payload:dict):

    expire_time = datetime.now() + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE)

    to_encode = payload.copy()
    to_encode.update({"exp":expire_time})

    refresh_token = jwt.encode(payload=to_encode, key=settings.KEY, algorithm=settings.ALGORITHM)

    return refresh_token


def password_verify(user_entered_password, db_hashed_password):
    return password_util.verify(user_entered_password, db_hashed_password)


developer_oauth_schema = OAuth2PasswordBearer(tokenUrl="developers/login", scheme_name="Developers")
api_from_header = APIKeyHeader(name="API from header", auto_error=True)

def decode_token(token:str):
    decoded_token = jwt.decode(token, algorithms=[settings.ALGORITHM], key=settings.KEY)
    return decoded_token

async def get_developer_Byemail(email:str, db:AsyncSession):
    stmt = select(Developers).where(Developers.email == email)
    result = await db.execute(stmt)
    developer = result.scalar_one_or_none()

    return developer


async def get_current_developer(access_token:str=Depends(developer_oauth_schema), db:AsyncSession=Depends(get_session)):

    redis_key = f"access_token:{access_token}"
    cached_developer_payload = await redis_client.get(redis_key)

    if cached_developer_payload:
        cached_payload = json.loads(str(cached_developer_payload))
        developer_email = cached_payload.get("email")
        developer = await get_developer_Byemail(developer_email, db)
        return developer


    payload = decode_token(token=access_token)

    developer_email = payload.get("email")

    if developer_email is None:
        raise HTTPException(status_code=401, detail="Invalid details")

    developer = await get_developer_Byemail(email=developer_email, db=db)

    return developer

