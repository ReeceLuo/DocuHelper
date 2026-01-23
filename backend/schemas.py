from pydantic import BaseModel, ConfigDict, Field
from typing import Optional



class UserCreate(BaseModel):
    name: str = Field(min_length = 3, max_length = 30, pattern = r"^[a-zA-Z\s]+$")
    email: str = Field(min_length = 1)
    password: str = Field(min_length = 3, max_length = 50)

class UserResponse(BaseModel):
    name: str
    email: str

    model_config = ConfigDict(from_attributes = True)