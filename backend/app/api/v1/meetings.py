from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.meeting import MeetingCreate, MeetingUpdate, MeetingRead
from app.api.v1.skills import check_admin_or_lead_role
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.meeting import Meeting, MeetingAssessment
from app.models.skill import PlanItem
from app.schemas.skill import SkillStatusEnum

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
    db_meeting = Meeting(
        interviewer_id=current_user.id,
        participant_id=meeting_in.participant_id,
        meeting_date=meeting_in.meeting_date,
        summary_markdown=meeting_in.summary_markdown,
        files_and_links=meeting_in.files_and_links
    )
    db.add(db_meeting)
    await db.flush()

    for assess in meeting_in.assessments:
        db_assess = MeetingAssessment(
            meeting_id=db_meeting.id,
            skill_id=assess.skill_id,
            is_completed=assess.is_completed,
            has_problem=assess.has_problem,
            comment=assess.comment
        )
        db.add(db_assess)

        query = select(PlanItem).where(
            PlanItem.user_id == meeting_in.participant_id,
            PlanItem.skill_id == assess.skill_id
        )
        result = await db.execute(query)
        plan_item = result.scalar_one_or_none()

        if plan_item:
            if assess.is_completed:
                plan_item.status = SkillStatusEnum.COMPLETED
                plan_item.confirmed_at = date.today()
            elif assess.has_problem:
                plan_item.status = SkillStatusEnum.PROBLEM
                plan_item.problem_comment = assess.comment

    await db.commit()
    await db.refresh(db_meeting)
    return db_meeting


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
    query = select(Meeting)
    if participant_id is not None:
        query = query.where(Meeting.participant_id == participant_id)
    if interviewer_id is not None:
        query = query.where(Meeting.interviewer_id == interviewer_id)

    result = await db.execute(query)
    return result.scalars().all()


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
    result = await db.execute(select(Meeting).where(Meeting.id == meeting_id))
    db_meeting = result.scalar_one_or_none()

    if db_meeting is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Протокол встречи не найден"
        )

    fields = meeting_in.model_fields_set
    if "meeting_date" in fields:
        db_meeting.meeting_date = meeting_in.meeting_date
    if "summary_markdown" in fields:
        db_meeting.summary_markdown = meeting_in.summary_markdown
    if "files_and_links" in fields:
        db_meeting.files_and_links = meeting_in.files_and_links

    await db.commit()
    await db.refresh(db_meeting)
    return db_meeting
