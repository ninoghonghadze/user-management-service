import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.user import Group, User, UserRole
from app.db.session import get_db
from app.schemas.user import GroupCreate, GroupResponse
from app.api.users import get_current_user, require_admin

router = APIRouter(prefix="/groups", tags=["Groups"])


@router.post("/", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(
    group_data: GroupCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    # Only admin can create groups
    group = Group(name=group_data.name)
    db.add(group)
    await db.commit()
    await db.refresh(group)
    return group


@router.get("/", response_model=list[GroupResponse])
async def get_groups(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    # Only admin can list all groups
    result = await db.execute(select(Group))
    return result.scalars().all()

@router.post("/{group_id}/users/{user_id}", response_model=GroupResponse)
async def add_user_to_group(
    group_id: uuid.UUID,
    user_id: uuid.UUID,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    # Only admin can assign users to groups
    group = await db.get(Group, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.group_id = group_id
    await db.commit()
    await db.refresh(group)
    return group