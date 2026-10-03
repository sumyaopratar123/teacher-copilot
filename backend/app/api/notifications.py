from fastapi import APIRouter, HTTPException
from typing import Optional
from app.core.supabase_client import get_supabase

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("")
async def get_notifications(user_id: str):
    """Get notifications for a user"""
    supabase = get_supabase()
    
    try:
        response = supabase.table("notifications").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{notification_id}/read")
async def mark_as_read(notification_id: str):
    """Mark a notification as read"""
    supabase = get_supabase()
    
    try:
        response = supabase.table("notifications").update({
            "read": True
        }).eq("id", notification_id).execute()
        
        return {"message": "Notification marked as read"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/user/{user_id}/read-all")
async def mark_all_as_read(user_id: str):
    """Mark all notifications as read for a user"""
    supabase = get_supabase()
    
    try:
        response = supabase.table("notifications").update({
            "read": True
        }).eq("user_id", user_id).execute()
        
        return {"message": "All notifications marked as read"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("")
async def create_notification(
    user_id: str,
    title: str,
    message: str,
    type: str = "info",
    action_url: Optional[str] = None
):
    """Create a notification (internal use)"""
    supabase = get_supabase()
    
    try:
        notification_data = {
            "user_id": user_id,
            "title": title,
            "message": message,
            "type": type,
            "action_url": action_url
        }
        
        response = supabase.table("notifications").insert(notification_data).execute()
        
        return response.data[0] if response.data else {"message": "Notification created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
