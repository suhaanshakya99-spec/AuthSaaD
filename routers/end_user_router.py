from fastapi import (APIRouter, Depends)
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import (OAuth2PasswordRequestForm)
from models.postgres_models import (Developers, Projects, End_Users)
from services.project_services import (create_project, fetch_all_projects, update_project, delete_project)
from schemas.project_schemas import (CreateProject, UpdateProject)
from dependency.db import (get_session)
from core.auth import (get_current_developer, get_current_user, verify_user_refresh_token)
from dependency.API import (api_key_header)
from schemas.end__user_schemas import (CreateEndUser)
from dependency.API import verify_api_key
from services.end_users_services import (create_user, login, verify_verification_token, delete_user)

router = APIRouter(prefix="/end-user", tags=["End-User"])

#ap3R5ilhjTRhYRFEH4w1YcItlIvFBrwtzOX2AZU9DuU

@router.post("/new-user")
async def register_new_user(data:CreateEndUser, api_key:str=Depends(api_key_header), db:AsyncSession=Depends(get_session)):
    result = await create_user(api_key, db, data)
    return result


@router.post("/login")
async def login_end_user(data=Depends(OAuth2PasswordRequestForm), db:AsyncSession=Depends(get_session), api_key=Depends(api_key_header)):
    result = await login(api_key, data, db)
    return result


@router.post("/verification")
async def verification_of_user(token:str, db:AsyncSession= Depends(get_session), api:str=Depends(api_key_header), end_user:End_Users=Depends(get_current_user)):
    result = await verify_verification_token(api, token, db, end_user)
    return result

@router.delete("/delete")
async def destroy_user(api:str=Depends(api_key_header), end_user:End_Users=Depends(get_current_user), db:AsyncSession=Depends(get_session)):
    result = await delete_user(api, end_user, db)
    return result

@router.post("/refresh-token")
async def refresh_token(api_key:str, refresh_token:str, db:AsyncSession=Depends(get_session)):

    await verify_api_key(db, api_key)

    result = await verify_user_refresh_token(refresh_token, db)
    return result