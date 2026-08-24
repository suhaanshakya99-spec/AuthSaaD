from fastapi import (Depends, HTTPException)
from sqlalchemy.ext.asyncio import AsyncSession
import json
from sqlalchemy import (select)
from fastapi.security import OAuth2PasswordRequestForm
import secrets
from schemas.developer_schemas import (CreateDeveloper, CreateProject)
from core.auth import (hash_password, create_access_token, create_refresh_token, password_verify, get_current_developer)
from models.postgres_models import (Developers, Projects)
from core.redis_client import redis_client
from core.celery import (sending_verification_mail)



async def register_developer(data:CreateDeveloper, db:AsyncSession):

    hashed_password = hash_password(data.plain_password)

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

    sending_verification_mail.delay(new_developer.email, 'This is Verification Link')

    return response


async def login_develepor(data:OAuth2PasswordRequestForm, db:AsyncSession):
    developer_email = data.username

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

    raise HTTPException(status_code=401, detail="Developer details invalid.")

#Create a project
async def create_project(data:CreateProject, db:AsyncSession, developer:Developers):

    plain_API = secrets.token_urlsafe(32)

    project = Projects(project_name=data.project_name, developer_id=developer.id, api=plain_API)

    db.add(project)
    await db.commit()
    await db.refresh(project)

    result = {"project_id":project.id,
              "developer_id":project.developer,
              "API":plain_API}

    return result

