from fastapi import (APIRouter, Depends)
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import (OAuth2PasswordRequestForm)
from models.postgres_models import (Developers, Projects)
from services.project_services import (create_project, fetch_all_projects, update_project, delete_project)
from schemas.project_schemas import (CreateProject, UpdateProject)
from dependency.db import (get_session)
from core.auth import (get_current_developer, api_from_header)
from schemas.end__user_schemas import (CreateEndUser)

router = APIRouter(prefix="/developers/projects", tags=["Projects"])


@router.post("/project")
async def open_new_project(data:CreateProject, developer:Developers=Depends(get_current_developer), db:AsyncSession=Depends(get_session)):
    result = await create_project(data, db, developer)
    return result


@router.get("")
async def view_all_projects(developer:Developers=Depends(get_current_developer), db:AsyncSession=Depends(get_session)):
    result = await fetch_all_projects(id=developer.id, db=db)
    return result



@router.put("/update/{project_id}")
async def update_project_name(data:UpdateProject, project_id:int, db:AsyncSession=Depends(get_session), developer:Developers=Depends(get_current_developer)):
    result = await update_project(data, project_id, db, developer.id)
    return result


@router.delete("/delete/{project_id}")
async def destroy_project(project_id:int, db:AsyncSession=Depends(get_session), developer:Developers=Depends(get_current_developer),):
    result = await delete_project(project_id, db, developer.id)
    return result

