from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

# Убрали неиспользуемый SkillAssessment, оставили только нужные схемы
from app.schemas.meeting import MeetingCreate, MeetingUpdate, MeetingRead
from app.core.database import get_db  # Общая зависимость сессии БД из архитектуры

router = APIRouter(tags=["Проведение 1:1 встреч (PR-протоколы)"])


# --- Заглушка авторизации руководителя (Лида) ---
async def check_lead_role():
    """
    Проверяет, что встречу создает именно Руководитель,
    а не обычный сотрудник (защита эндпоинтов).
    """
    return True


# --- Эндпоинты Встреч ---

@router.post(
    "/meetings",
    response_model=MeetingRead,
    status_code=status.HTTP_201_CREATED,
    summary="Сохранить новый протокол 1:1 встречи"
)
async def create_meeting(
        meeting_in: MeetingCreate,
        db: AsyncSession = Depends(get_db),
        is_lead: bool = Depends(check_lead_role)
):
    """
    Создание протокола встречи 1:1.
    Принимает Markdown-итоги, файлы и список оценок скиллов.
    Доступно **только Руководителю (Лиду)**.
    """
    # Идентификатор руководителя (интервьюера) берем из авторизации (пока мок = 99)
    mock_interviewer_id = 99

    return MeetingRead(
        id=501,
        interviewer_id=mock_interviewer_id,
        participant_id=meeting_in.participant_id,
        meeting_date=meeting_in.meeting_date,
        summary_markdown=meeting_in.summary_markdown,
        files_and_links=meeting_in.files_and_links
    )


@router.get(
    "/meetings",
    response_model=List[MeetingRead],
    summary="Получить историю 1:1 встреч"
)
async def get_meetings_history(
        participant_id: Optional[int] = None,
        interviewer_id: Optional[int] = None,
        db: AsyncSession = Depends(get_db)
):
    """
    Получение списка (истории) протоколов встреч.
    Можно фильтровать по participant_id или по interviewer_id.
    """
    return [
        MeetingRead(
            id=501,
            interviewer_id=interviewer_id or 99,
            participant_id=participant_id or 12,
            meeting_date=datetime.now(),
            summary_markdown="# Итоги Performance Review\nСотрудник показывает отличный рост.",
            files_and_links=["https://company.com"]
        )
    ]


@router.patch(
    "/meetings/{meeting_id}",
    response_model=MeetingRead,
    summary="Редактировать существующий протокол встречи"
)
async def update_meeting(
        meeting_id: int,
        meeting_in: MeetingUpdate,
        db: AsyncSession = Depends(get_db),
        is_lead: bool = Depends(check_lead_role)
):
    """
    Редактирование протокола 1:1 встречи.
    Доступно **только Руководителю**, который эту встречу создал.
    """
    return MeetingRead(
        id=meeting_id,
        interviewer_id=99,
        participant_id=12,
        meeting_date=meeting_in.meeting_date or datetime.now(),
        summary_markdown=meeting_in.summary_markdown or "# Обновленный Markdown",
        files_and_links=meeting_in.files_and_links or []
    )
