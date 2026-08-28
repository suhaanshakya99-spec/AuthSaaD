from fastapi import (Depends, HTTPException)
from sqlalchemy.ext.asyncio import AsyncSession
import json
from sqlalchemy import (select, delete)
from fastapi.security import OAuth2PasswordRequestForm
import secrets
from schemas.project_schemas import (UpdateProject, CreateProject)
from schemas.end__user_schemas import (CreateEndUser)
from core.auth import (hash_password, create_access_token, create_refresh_token, password_verify, get_current_developer)
from models.postgres_models import (Developers, Projects, End_Users, Tokens)
from core.redis_client import redis_client
from core.celery import (sending_verification_mail)

#apikey = TN-hkj8IIaAXqY61umNkGEfmniobj0eVhOZuRZaWjFg


#Create a project
async def create_project(data:CreateProject, db:AsyncSession, developer:Developers)->dict:

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




async def update_project(data:UpdateProject, project_id:int, db:AsyncSession, developer_id:int):

    stmt = select(Projects).where(Projects.id==project_id, Projects.developer_id==developer_id)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()

    if project is None:
        raise HTTPException(status_code=404, detail="project not found.")

    if data.new_name is not None:
        project.project_name = data.new_name

    await db.commit()

    return project



async def delete_project(project_id:int, db:AsyncSession, developer_id:int):

    stmt = select(Projects).where(Projects.id==project_id, Projects.developer_id==developer_id)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()

    if project is None:
        raise HTTPException(status_code=404, detail="project not found.")

    stmt = delete(Projects).where(Projects.id == project_id)
    result = await db.execute(stmt)

    await db.commit()

    return {"message":"Project delete successfully"}
