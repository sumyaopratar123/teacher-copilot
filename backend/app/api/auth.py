from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.core.supabase_client import get_supabase

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    user: dict
    session: dict
    profile: dict


@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    """Register a new user (teacher or student)"""
    supabase = get_supabase()
    
    try:
        # Register with Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password,
            "options": {
                "data": {
                    "full_name": request.full_name,
                    "role": request.role
                }
            }
        })
        
        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration failed"
            )
        
        # Create profile
        profile_data = {
            "id": auth_response.user.id,
            "email": request.email,
            "full_name": request.full_name,
            "role": request.role
        }
        
        profile_response = supabase.table("profiles").insert(profile_data).execute()
        
        return AuthResponse(
            user=auth_response.user.model_dump(),
            session=auth_response.session.model_dump() if auth_response.session else {},
            profile=profile_response.data[0] if profile_response.data else profile_data
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """Login user"""
    supabase = get_supabase()
    
    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        
        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Get profile
        profile_response = supabase.table("profiles").select("*").eq("id", auth_response.user.id).execute()
        
        if not profile_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        return AuthResponse(
            user=auth_response.user.model_dump(),
            session=auth_response.session.model_dump(),
            profile=profile_response.data[0]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post("/logout")
async def logout():
    """Logout user"""
    supabase = get_supabase()
    supabase.auth.sign_out()
    return {"message": "Logged out successfully"}


@router.get("/profile")
async def get_profile(token: str):
    """Get user profile from token"""
    supabase = get_supabase()
    
    try:
        supabase.auth.set_session(token, token)
        user = supabase.auth.get_user()
        
        if not user.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        profile_response = supabase.table("profiles").select("*").eq("id", user.user.id).execute()
        
        if not profile_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        return profile_response.data[0]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
