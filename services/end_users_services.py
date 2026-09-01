from fastapi import (Depends, HTTPException)
from sqlalchemy.ext.asyncio import AsyncSession
import json
from sqlalchemy import (select, delete)
from fastapi.security import OAuth2PasswordRequestForm
import secrets
from schemas.project_schemas import (UpdateProject, CreateProject)
from schemas.end__user_schemas import (CreateEndUser, UpdateEndUser)
from core.auth import (hash_password, create_access_token, create_refresh_token, password_verify, get_current_developer, enduser_oauth_schema)
from models.postgres_models import (Developers, Projects, End_Users, Tokens)
from core.redis_client import redis_client
from core.celery import (sending_verification_mail, send_user_verificationmail)
from services.project_services import (fetch_all_projects)
from dependency.API import verify_api_key
from datetime import (datetime, timedelta, timezone)


#Create a user for project by developer using our shi
async def create_user(api_key:str, db:AsyncSession, data:CreateEndUser)->dict:

    project = await verify_api_key(db, api_key)

    plain_password = data.plain_password
    hashed_password = hash_password(plain_password)

    end_user = End_Users(email=data.email, name=data.name, user_end_hashedpass=hashed_password, project_id=project.get("project_id"))
    db.add(end_user)
    await db.commit()
    await db.refresh(end_user)

    payload = {"id":end_user.id, "email":end_user.email}

    access_token = create_access_token(payload)
    refresh_token = create_refresh_token(payload)

    verification_token = secrets.token_urlsafe(32)
    hashed_verfication_token = hash_password(verification_token)
    print(verification_token)

    token = Tokens(end_user_id=end_user.id, token_hashed=hashed_verfication_token, token_type="Verification")
    db.add(token)
    await db.commit()

    send_user_verificationmail.delay(end_user.email, verification_token)

    response =  {"access_token":access_token, "refresh_token":refresh_token, "token_type":"bearer"}

    redis_name = f"end_user_access_token:{access_token}"
    redis_dict = {"id":end_user.id, "email":end_user.email, "project_id":end_user.project_id}
    json_encoded_redis = json.dumps(redis_dict)
    await redis_client.set(name=redis_name, value=json_encoded_redis, ex=300)

    return response


async def login(api_key:str, data:OAuth2PasswordRequestForm, db:AsyncSession):

    project = await verify_api_key(db, api_key)

    login_email = data.username

    stmt = select(End_Users).where(End_Users.email == login_email, End_Users.project_id==project.get("project_id"))
    result = await db.execute(stmt)
    end_user = result.scalar_one_or_none()

    if end_user is None:
        raise HTTPException(status_code=401, detail="wrong credentials")

    result = password_verify(data.password, end_user.user_end_hashedpass)

    if result:
        payload = payload = {"id":end_user.id, "email":end_user.email}

        access_token = create_access_token(payload)
        refresh_token = create_refresh_token(payload)

        redis_name = f"access_token:{access_token}"
        redis_dict = {"id":end_user.id, "email":end_user.email, "project_id":end_user.project_id}
        json_encoded = json.dumps(redis_dict)

        await redis_client.set(name=redis_name, value=json_encoded, ex=300)

        response =  {"access_token":access_token, "refresh_token":refresh_token, "token_type":"bearer"}

        return response


async def verify_verification_token(api:str, token:str, db:AsyncSession, end_user:End_Users):

    await verify_api_key(db, api)

    stmt = select(Tokens).where(Tokens.end_user_id == end_user.id, Tokens.token_type == "Verification").order_by(Tokens.created_at.desc())
    result = await db.execute(stmt)
    enduser = result.scalar_one_or_none()

    if enduser is None:
        raise HTTPException(status_code=404, detail="user not in db")

    if enduser.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="token has expired")

    if not password_verify(token, enduser.token_hashed):
        raise HTTPException(status_code=401, detail="invalid token")

    end_user.verified = True
    enduser.used_at = datetime.now(timezone.utc)

    return {"message":"user has been verified"}