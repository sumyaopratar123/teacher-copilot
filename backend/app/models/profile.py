from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class ProfileBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: str
    avatar_url: Optional[str] = None


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None


class Profile(ProfileBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
