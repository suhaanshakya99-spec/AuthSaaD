from fastapi import (APIRouter, Depends)
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import (OAuth2PasswordRequestForm)
from models.postgres_models import (Developers, Projects)
from services.API_services import (create_project, fetch_all_projects)
from schemas.developer_schemas import (CreateDeveloper, CreateProject)
from dependency.db import (get_session)
from core.auth import (get_current_developer)

router = APIRouter(prefix="/developers/projects", tags=["API"])


@router.post("/project")
async def open_new_project(data:CreateProject, developer:Developers=Depends(get_current_developer), db:AsyncSession=Depends(get_session)):
    result = await create_project(data, db, developer)
    return result


@router.post("")
async def view_all_projects(developer:Developers=Depends(get_current_developer), db:AsyncSession=Depends(get_session)):
    result = await fetch_all_projects(id=developer.id, db=db)
    return result