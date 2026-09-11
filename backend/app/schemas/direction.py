from pydantic import BaseModel, ConfigDict, Field


class DirectionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, examples=["BACK"])


class DirectionCreate(DirectionBase):
    pass


class DirectionUpdate(DirectionBase):
    pass


class DirectionRead(DirectionBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
