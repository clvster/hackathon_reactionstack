from typing import Optional

from pydantic import BaseModel, ConfigDict


class DepartmentCreate(BaseModel):
    name: str
    parent_id: Optional[int] = None
    leader_id: Optional[int] = None


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None
    leader_id: Optional[int] = None


class DepartmentResponse(BaseModel):
    id: int
    name: str
    parent_id: Optional[int]
    leader_id: Optional[int]

    model_config = ConfigDict(from_attributes=True)


class DepartmentTreeResponse(BaseModel):
    id: int
    name: str
    parent_id: Optional[int]
    leader_id: Optional[int]
    children: list["DepartmentTreeResponse"] = []

    model_config = ConfigDict(from_attributes=True)