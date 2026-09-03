from fastapi import (Depends, HTTPException, Body)
from sqlalchemy.ext.asyncio import AsyncSession
import json
from sqlalchemy import (select)
from fastapi.security import OAuth2PasswordRequestForm
import secrets
from schemas.developer_schemas import (CreateDeveloper)
from core.auth import (hash_password, create_access_token, create_refresh_token, password_verify, get_current_developer)
from models.postgres_models import (Developers, Projects, Tokens)
from core.redis_client import (redis_client, ratelimiting)
from core.celery import (sending_verification_mail)
import secrets
from datetime import datetime, timezone


async def register_developer(data:CreateDeveloper, db:AsyncSession):

    hashed_password = hash_password(data.plain_password)

    stmt = select(Developers).where(Developers.email==data.email)
    result = await db.execute(stmt)
    developer_db = result.scalar_one_or_none()

    if developer_db:
        raise HTTPException(status_code=409, detail="email already registered")

    new_developer = Developers(email=data.email, hash_password=hashed_password)

    db.add(new_developer)
    await db.commit()
    await db.refresh(new_developer)

    payload = {"id":new_developer.id, "email":new_developer.email}

    access_token = create_access_token(payload=payload)
    refresh_token = create_refresh_token(payload=payload)

    response = {"access_token":access_token, "refresh_token":refresh_token, "token_type":"bearer"}

    redis_key = f"developer_access_token:{access_token}"
    await redis_client.set(name=redis_key, value=str(new_developer.email), ex=300)

    verification_token = secrets.token_urlsafe(32)
    hashed_token = hash_password(verification_token)
    print(verification_token)

    token = Tokens(developer_id=new_developer.id, token_hashed=hashed_token, token_type="Verification")

    db.add(token)
    await db.commit()

    sending_verification_mail.delay(verification_token, new_developer.email)

    return response


async def login_develepor(data:OAuth2PasswordRequestForm, db:AsyncSession):

    developer_email = data.username

    await ratelimiting(developer_email)

    stmt = select(Developers).where(Developers.email == developer_email)
    result = await db.execute(stmt)
    developer = result.scalar_one_or_none()

    if developer is None:
        raise HTTPException(status_code=404, detail="Developer not in db.")
    
    developer_hashed_password = developer.hash_password

    if password_verify(data.password, developer_hashed_password):
            
        payload = {"id":developer.id, "email":developer.email}

        access_token = create_access_token(payload=payload)
        refresh_token = create_refresh_token(payload=payload)

        response = {"access_token":access_token, "refresh_token":refresh_token, "token_type":"bearer"}

   
        redis_key = f"access_token:{access_token}"
        await redis_client.set(name=redis_key, value=json.dumps(payload), ex=300)

        return response

    raise HTTPException(status_code=401, detail="developer credential is wrong")



async def verify_verification_token(token:str, db:AsyncSession, developer:Developers):

    stmt = select(Tokens).where(Tokens.developer_id==developer.id, Tokens.token_type=="Verification", Tokens.used_at==None).order_by(Tokens.created_at.desc())
    result = await db.execute(stmt)
    token_from_db = result.scalar_one_or_none()

    if token_from_db is None:
        raise HTTPException(status_code=404, detail="developer not found")

    if token_from_db.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="verfication has expired")

    if password_verify(token, token_from_db.token_hashed):
        token_from_db.used_at = datetime.now(timezone.utc)
        developer.verified = True
        await db.commit()

    return {"message":"Verification done"}


async def delete_developer(developer:Developers, db:AsyncSession):

    developer_id = developer.id

    stmt = select(Developers).where(Developers.id==developer_id)
    result = await db.execute(stmt)
    db_developer = result.scalar_one_or_none()

    if db_developer is None:
        raise HTTPException(status_code=404, detail="developer not found in db")

    await db.delete(db_developer)
    await db.commit()

    return {"message":"developer deleted from db."}


