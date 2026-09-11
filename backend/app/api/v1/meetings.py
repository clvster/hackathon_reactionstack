from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.meeting import MeetingCreate, MeetingUpdate, MeetingRead
from app.api.v1.skills import check_admin_or_lead_role
from app.api.deps import get_db, get_current_user
from app.models.user import User

router = APIRouter(tags=["Проведение 1:1 встреч (PR-протоколы)"])


@router.post(
    "/meetings",
    response_model=MeetingRead,
    status_code=status.HTTP_201_CREATED,
    summary="Сохранить новый протокол 1:1 встречи"
)
async def create_meeting(
    meeting_in: MeetingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(check_admin_or_lead_role)
):
    return MeetingRead(
        id=501,
        interviewer_id=current_user.id,
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
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return [
        MeetingRead(
            id=501,
            interviewer_id=interviewer_id or current_user.id,
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
    current_user: User = Depends(check_admin_or_lead_role)
):
    return MeetingRead(
        id=meeting_id,
        interviewer_id=current_user.id,
        participant_id=12,
        meeting_date=meeting_in.meeting_date or datetime.now(),
        summary_markdown=meeting_in.summary_markdown or "# Обновленный Markdown",
        files_and_links=meeting_in.files_and_links or []
    )
