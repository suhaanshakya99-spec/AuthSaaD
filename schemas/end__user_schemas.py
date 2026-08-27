from pydantic import (BaseModel, EmailStr)

class CreateEndUser(BaseModel):
    email:EmailStr
    name:str
    plain_password:str
