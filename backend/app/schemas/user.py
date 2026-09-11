from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict


Direction = Literal["BACK", "FRONT", "QA"]


class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    direction: Direction
    department_id: Optional[int] = None
    is_admin: bool = False


class UserUpdate(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    full_name: Optional[str] = None
    direction: Optional[Direction] = None
    department_id: Optional[int] = None
    is_admin: Optional[bool] = None


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    direction: str
    department_id: Optional[int]
    is_admin: bool

    model_config = ConfigDict(from_attributes=True)