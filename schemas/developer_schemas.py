from pydantic import (BaseModel, ConfigDict, EmailStr)

class CreateDeveloper(BaseModel):
    email:EmailStr
    plain_password:str

class CreateProject(BaseModel):
    project_name:str