from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

from app.db.models.user import UserRole


class UserCreate(BaseModel):
    name: str
    surname: str
    username: str
    email: EmailStr
    password: str
    phone_number: Optional[str] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    image_s3_path: Optional[str] = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    surname: str
    username: str
    email: str
    phone_number: Optional[str] = None
    role: UserRole
    image_s3_path: Optional[str] = None
    is_blocked: bool
    created_at: datetime
    modified_at: datetime
    group_id: Optional[UUID] = None


class GroupCreate(BaseModel):
    name: str


class GroupResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    created_at: datetime
