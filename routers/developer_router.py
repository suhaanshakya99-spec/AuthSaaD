from fastapi import (APIRouter, Depends)
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import (OAuth2PasswordRequestForm)
from models.postgres_models import (Developers, Projects)
from services.developer_services import (register_developer, login_develepor, verify_verification_token)
from schemas.developer_schemas import (CreateDeveloper, CreateProject)
from dependency.db import (get_session)
from core.auth import (get_current_developer)

router = APIRouter(prefix="/developers", tags=["Developer"])

@router.post("/registration")
async def developer_registration(data:CreateDeveloper, db:AsyncSession=Depends(get_session))->dict:
    result = await register_developer(data, db)
    return result

@router.post("/login")
async def developers_login(data:OAuth2PasswordRequestForm=Depends(), db:AsyncSession=Depends(get_session)):
    result = await login_develepor(data, db)
    return result


@router.post("/verify-developer")
async def verifydeveloper(token:str, developer:Developers=Depends(get_current_developer), db:AsyncSession=Depends(get_session)):
    result = await verify_verification_token(token, db, developer)
    return result
