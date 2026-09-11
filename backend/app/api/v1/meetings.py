from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, get_db
from app.models.meeting import Meeting, MeetingAssessment
from app.models.skill import PlanItem, Skill
from app.models.user import User
from app.schemas.meeting import MeetingCreate, MeetingRead, MeetingUpdate, SkillAssessment
from app.schemas.skill import SkillStatusEnum
from app.services.access import require_manage_user, require_view_user
from app.services.tree_services import get_visible_user_ids

router = APIRouter(tags=["Встречи 1:1 (PR-протоколы)"])


def to_naive_utc(value: datetime) -> datetime:
    if value.tzinfo is not None:
        return value.astimezone(timezone.utc).replace(tzinfo=None)
    return value


async def load_meeting(db: AsyncSession, meeting_id: int) -> Meeting:
    result = await db.execute(
        select(Meeting)
        .options(selectinload(Meeting.assessments))
        .where(Meeting.id == meeting_id)
        .execution_options(populate_existing=True)
    )
    meeting = result.scalar_one_or_none()
    if meeting is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Протокол встречи не найден")
    return meeting


async def apply_assessments(
    db: AsyncSession,
    meeting: Meeting,
    assessments: List[SkillAssessment],
) -> None:
    skill_ids = [a.skill_id for a in assessments]
    if len(skill_ids) != len(set(skill_ids)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Скилл оценён в протоколе несколько раз")
    if skill_ids:
        found = await db.scalars(select(Skill.id).where(Skill.id.in_(skill_ids)))
        missing = set(skill_ids) - set(found.all())
        if missing:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Скиллы не найдены: {sorted(missing)}")

    meeting_day = meeting.meeting_date.date()
    for assessment in assessments:
        if assessment.is_completed and assessment.has_problem:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Скилл не может быть одновременно подтверждён и проблемным",
            )
        meeting.assessments.append(
            MeetingAssessment(
                skill_id=assessment.skill_id,
                is_completed=assessment.is_completed,
                has_problem=assessment.has_problem,
                comment=assessment.comment,
            )
        )

        plan_item = await db.scalar(
            select(PlanItem).where(
                PlanItem.user_id == meeting.participant_id,
                PlanItem.skill_id == assessment.skill_id,
            )
        )
        if plan_item is None:
            plan_item = PlanItem(
                user_id=meeting.participant_id,
                skill_id=assessment.skill_id,
                target_date=meeting_day,
                status=SkillStatusEnum.PLANNED,
            )
            db.add(plan_item)

        if assessment.is_completed:
            plan_item.status = SkillStatusEnum.COMPLETED
            plan_item.confirmed_at = meeting_day
            plan_item.problem_comment = None
        elif assessment.has_problem:
            plan_item.status = SkillStatusEnum.PROBLEM
            plan_item.problem_comment = assessment.comment
        elif plan_item.status == SkillStatusEnum.PLANNED:
            plan_item.status = SkillStatusEnum.TRAINING


@router.post(
    "/meetings",
    response_model=MeetingRead,
    status_code=status.HTTP_201_CREATED,
    summary="Сохранить протокол встречи 1:1",
)
async def create_meeting(
    meeting_in: MeetingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await require_manage_user(db, current_user, meeting_in.participant_id)

    meeting = Meeting(
        interviewer_id=current_user.id,
        participant_id=meeting_in.participant_id,
        meeting_date=to_naive_utc(meeting_in.meeting_date),
        summary_markdown=meeting_in.summary_markdown,
        files_and_links=meeting_in.files_and_links,
        problem_comment=meeting_in.global_problem_comment,
        assessments=[],
    )
    db.add(meeting)
    await apply_assessments(db, meeting, meeting_in.assessments)
    await db.commit()
    return await load_meeting(db, meeting.id)


@router.get("/meetings", response_model=List[MeetingRead], summary="История встреч 1:1")
async def list_meetings(
    participant_id: Optional[int] = None,
    interviewer_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Meeting).options(selectinload(Meeting.assessments))
    if not current_user.is_admin:
        visible_ids = await get_visible_user_ids(db=db, current_user_id=current_user.id, is_admin=False)
        query = query.where(Meeting.participant_id.in_(visible_ids))
    if participant_id is not None:
        query = query.where(Meeting.participant_id == participant_id)
    if interviewer_id is not None:
        query = query.where(Meeting.interviewer_id == interviewer_id)
    result = await db.execute(query.order_by(Meeting.meeting_date.desc(), Meeting.id.desc()))
    return result.scalars().all()


@router.get("/meetings/{meeting_id}", response_model=MeetingRead, summary="Протокол встречи")
async def get_meeting(
    meeting_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meeting = await load_meeting(db, meeting_id)
    await require_view_user(db, current_user, meeting.participant_id)
    return meeting


@router.patch("/meetings/{meeting_id}", response_model=MeetingRead, summary="Изменить протокол встречи")
async def update_meeting(
    meeting_id: int,
    meeting_in: MeetingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meeting = await load_meeting(db, meeting_id)
    await require_manage_user(db, current_user, meeting.participant_id)

    fields = meeting_in.model_fields_set
    if "meeting_date" in fields and meeting_in.meeting_date:
        meeting.meeting_date = to_naive_utc(meeting_in.meeting_date)
    if "summary_markdown" in fields and meeting_in.summary_markdown:
        meeting.summary_markdown = meeting_in.summary_markdown
    if "files_and_links" in fields and meeting_in.files_and_links is not None:
        meeting.files_and_links = meeting_in.files_and_links
    if "global_problem_comment" in fields:
        meeting.problem_comment = meeting_in.global_problem_comment
    if "assessments" in fields and meeting_in.assessments is not None:
        meeting.assessments.clear()
        await db.flush()
        await apply_assessments(db, meeting, meeting_in.assessments)

    await db.commit()
    return await load_meeting(db, meeting_id)


@router.delete(
    "/meetings/{meeting_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить протокол встречи",
)
async def delete_meeting(
    meeting_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meeting = await load_meeting(db, meeting_id)
    await require_manage_user(db, current_user, meeting.participant_id)
    await db.delete(meeting)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
