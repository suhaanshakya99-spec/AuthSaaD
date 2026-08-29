from pydantic import (BaseModel, EmailStr)

class CreateEndUser(BaseModel):
    email:EmailStr
    name:str
    plain_password:str


class UpdateEndUser(BaseModel):
    new_name:str