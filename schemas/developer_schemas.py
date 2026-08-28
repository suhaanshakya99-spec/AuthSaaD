from pydantic import (BaseModel, ConfigDict, EmailStr)

class CreateDeveloper(BaseModel):
    email:EmailStr
    plain_password:str

