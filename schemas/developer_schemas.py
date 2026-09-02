from pydantic import (BaseModel, ConfigDict, EmailStr)

class CreateDeveloper(BaseModel):
    email:EmailStr
    plain_password:str

class DeveloperToken(BaseModel):
    token:str