from pydantic import BaseModel


class PermissionsResponse(BaseModel):
    user_id: int
    is_admin: bool
    visible_department_ids: list[int]
    visible_user_ids: list[int]