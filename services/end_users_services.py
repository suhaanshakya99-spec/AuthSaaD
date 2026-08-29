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
from core.celery import (sending_verification_mail)
from services.project_services import (fetch_all_projects)


#api key validation
async def validate_api(api_key:str, db:AsyncSession, developer:Developers):
    developer_id = developer.id

    projects = await fetch_all_projects(db, developer_id)

    for project in projects:
        if project.api == api_key:
            print({"message":"Valid API key"})
            return project

    raise HTTPException(status_code=404, detail="API key not in db.")


#Create a user for project by developer using our shi
async def create_user(api_key:str, developer:Developers, db:AsyncSession, data:CreateEndUser)->dict:
    project = await validate_api(api_key, db, developer)

    plain_password = data.plain_password
    hashed_password = hash_password(plain_password)

    end_user = End_Users(email=data.email, name=data.name, user_end_hashedpass=hashed_password, project_id=project.id)
    db.add(end_user)
    await db.commit()
    await db.refresh(end_user)

    payload = {"id":end_user.id, "email":end_user.email}

    access_token = create_access_token(payload)
    refresh_token = create_refresh_token(payload)

    verification_token = secrets.token_urlsafe(32)
    hashed_verfication_token = hash_password(verification_token)

    token = Tokens(end_user_id=end_user.id, token_hashed=hashed_verfication_token, token_type="Verification")
    db.add(token)
    await db.commit()

    sending_verification_mail.delay(verification_token, end_user.email)

    response =  {"access_token":access_token, "refresh_token":refresh_token, "token_type":"bearer"}

    redis_name = f"end_user_access_token:{access_token}"
    redis_dict = {"id":end_user.id, "email":end_user.email, "project_id":end_user.project_id}
    json_encoded_redis = json.dumps(redis_dict)
    await redis_client.set(name=redis_name, value=json_encoded_redis, ex=300)

    return response


async def login(api_key:str, data:OAuth2PasswordRequestForm, db:AsyncSession):

    login_email = data.username

    stmt = select(End_Users).where(End_Users.email == login_email)
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