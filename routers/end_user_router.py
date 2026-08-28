from fastapi import (APIRouter, Depends)
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import (OAuth2PasswordRequestForm)
from models.postgres_models import (Developers, Projects)
from services.project_services import (create_project, fetch_all_projects, update_project, delete_project)
from schemas.project_schemas import (CreateProject, UpdateProject)
from dependency.db import (get_session)
from core.auth import (get_current_developer, api_from_header)
from schemas.end__user_schemas import (CreateEndUser)
from services.end_users_services import (create_user)

router = APIRouter(prefix="/end-user", tags=["End-User"])

@router.post("/end_user")
async def add_new_user(data:CreateEndUser, api_key:str=Depends(api_from_header), developer:Developers=Depends(get_current_developer), db:AsyncSession=Depends(get_session)):
    result = await create_user(api_key, developer, db, data)
    return result
