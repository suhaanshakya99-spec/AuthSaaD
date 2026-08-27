from fastapi import (Depends, HTTPException)
from sqlalchemy.ext.asyncio import AsyncSession
import json
from sqlalchemy import (select)
from fastapi.security import OAuth2PasswordRequestForm
import secrets
from schemas.developer_schemas import (CreateDeveloper, CreateProject)
from schemas.end__user_schemas import (CreateEndUser)
from core.auth import (hash_password, create_access_token, create_refresh_token, password_verify, get_current_developer)
from models.postgres_models import (Developers, Projects, End_Users, Tokens)
from core.redis_client import redis_client
from core.celery import (sending_verification_mail)

#apikey = TN-hkj8IIaAXqY61umNkGEfmniobj0eVhOZuRZaWjFg


#Create a project
async def create_project(data:CreateProject, db:AsyncSession, developer:Developers):

    plain_API = secrets.token_urlsafe(32)

    project = Projects(project_name=data.project_name, developer_id=developer.id, api=plain_API)

    db.add(project)
    await db.commit()
    await db.refresh(project)

    result = {"project_id":project.id,
              "developer_id":project.developer_id,
              "API":plain_API}

    await redis_client.set(name=plain_API, value=json.dumps(result), ex=300)

    return result


#developer sees all his projects
async def fetch_all_projects(db:AsyncSession, id:int):

    stmt = select(Projects).where(Projects.developer_id == id)
    result = await db.execute(stmt)
    projects = result.scalars().all()

    return projects


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