from fastapi import Depends, HTTPException, Path, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import jwt

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.services.tree_services import user_has_tree_access


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить токен",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        user_id = int(user_id)

    except (jwt.InvalidTokenError, ValueError, TypeError):
        raise credentials_exception

    result = await db.execute(
        select(User).where(User.id == user_id)
    )

    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


async def verify_tree_access(
    user_id: int = Path(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Проверяет, имеет ли текущий пользователь доступ
    к профилю target_user_id.

    Правила:
    - администратор имеет доступ ко всем;
    - пользователь имеет доступ к самому себе;
    - руководитель имеет доступ к пользователям
      в своём подразделении и его дочерних подразделениях.
    """

    if current_user.is_admin:
        return current_user

    has_access = await user_has_tree_access(
        db=db,
        current_user_id=current_user.id,
        target_user_id=user_id,
    )

    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к этому пользователю",
        )

    return current_user


async def ensure_can_manage_pr(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    target_user_id: int = None
) -> User:
    if current_user.id == target_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Сотрудник не может проводить Performance Review самому себе",
        )
    if not current_user.is_admin and not getattr(current_user, "is_lead", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для управления протоколами встреч",
        )
    return current_user
