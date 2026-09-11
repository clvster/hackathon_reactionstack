from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.permissions import PermissionsResponse
from app.services.tree_services import (
    get_visible_department_ids,
    get_visible_user_ids,
)

router = APIRouter(
    prefix="/permissions",
    tags=["Permissions"],
)


@router.get("/me", response_model=PermissionsResponse)
async def get_my_permissions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Отдаёт текущему пользователю его собственные права: какие
    подразделения и каких пользователей он может видеть/вести.

    Формат ответа соответствует тому, что уже ждёт фронтенд
    (frontend/src/api/permissions.ts, MOCK_PERMISSIONS) — этот
    эндпоинт можно подключать напрямую, без правок типов на фронте.
    """

    visible_user_ids = await get_visible_user_ids(
        db=db,
        current_user_id=current_user.id,
        is_admin=current_user.is_admin,
    )

    visible_department_ids = await get_visible_department_ids(
        db=db,
        current_user_id=current_user.id,
        is_admin=current_user.is_admin,
    )

    return PermissionsResponse(
        user_id=current_user.id,
        is_admin=current_user.is_admin,
        visible_department_ids=visible_department_ids,
        visible_user_ids=visible_user_ids,
    )