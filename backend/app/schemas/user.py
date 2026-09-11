from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


Direction = Literal["BACK", "FRONT", "QA"]


class UserCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=64)
    password: str = Field(..., min_length=6)
    full_name: str
    direction: Direction
    email: Optional[str] = None
    department_id: Optional[int] = None
    is_admin: bool = False


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=2, max_length=64)
    password: Optional[str] = Field(None, min_length=6)
    full_name: Optional[str] = None
    direction: Optional[Direction] = None
    email: Optional[str] = None
    department_id: Optional[int] = None
    is_admin: Optional[bool] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str]
    full_name: str
    direction: str
    department_id: Optional[int]
    is_admin: bool

    model_config = ConfigDict(from_attributes=True)