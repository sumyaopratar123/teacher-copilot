from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
from app.core.supabase_client import get_supabase
import os

router = APIRouter(prefix="/resources", tags=["resources"])


@router.post("/upload")
async def upload_resource(
    file: UploadFile = File(...),
    class_id: str = Form(...),
    uploader_id: str = Form(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    subject: Optional[str] = Form(None),
    topic: Optional[str] = Form(None),
    type: str = Form(...)
):
    """Upload a resource to Supabase Storage."""
    supabase = get_supabase()

    try:
        # Verify uploader exists
        profile_response = (
            supabase
            .table("profiles")
            .select("*")
            .eq("id", uploader_id)
            .execute()
        )

        if not profile_response.data:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        # Verify class exists
        class_response = (
            supabase
            .table("classes")
            .select("*")
            .eq("id", class_id)
            .execute()
        )

        if not class_response.data:
            raise HTTPException(
                status_code=404,
                detail="Class not found"
            )

        class_data = class_response.data[0]
        profile = profile_response.data[0]

        # Check uploader access
        if profile["role"] == "teacher":

            if class_data["teacher_id"] != uploader_id:
                raise HTTPException(
                    status_code=403,
                    detail="You can only upload to your own classes"
                )

        else:

            member_response = (
                supabase
                .table("class_members")
                .select("*")
                .eq("class_id", class_id)
                .eq("student_id", uploader_id)
                .execute()
            )

            if not member_response.data:
                raise HTTPException(
                    status_code=403,
                    detail="You can only upload to classes you're enrolled in"
                )

        # Read uploaded file
        file_content = await file.read()

        # Generate unique filename
        original_filename = file.filename or "uploaded_file"
        file_extension = os.path.splitext(original_filename)[1]

        unique_filename = (
            f"{class_id}_{uploader_id}_{original_filename}"
        )

        file_url = None

        # Upload to Supabase Storage
        try:
            storage = supabase.storage.from_("resources")

            storage_response = storage.upload(
                unique_filename,
                file_content,
                {
                    "content-type": file.content_type
                    or "application/octet-stream"
                }
            )

            # Get public URL
            file_url = storage.get_public_url(
                unique_filename
            )

        except Exception:
            # Storage failure should not prevent
            # database resource creation
            file_url = None

        # Create database record
        resource_data = {
            "class_id": class_id,
            "uploader_id": uploader_id,
            "title": title,
            "description": description,
            "type": type,
            "subject": subject,
            "topic": topic,
            "file_url": file_url
        }

        response = (
            supabase
            .table("resources")
            .insert(resource_data)
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=400,
                detail="Failed to create resource record"
            )

        return response.data[0]

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("")
async def get_resources(
    class_id: Optional[str] = None,
    uploader_id: Optional[str] = None
):
    """Get resources."""
    supabase = get_supabase()

    try:
        query = (
            supabase
            .table("resources")
            .select("*")
        )

        if class_id:
            query = query.eq("class_id", class_id)

        if uploader_id:
            query = query.eq("uploader_id", uploader_id)

        response = query.execute()

        return response.data

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/{resource_id}")
async def get_resource(resource_id: str):
    """Get a specific resource."""
    supabase = get_supabase()

    try:
        response = (
            supabase
            .table("resources")
            .select("*")
            .eq("id", resource_id)
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=404,
                detail="Resource not found"
            )

        return response.data[0]

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.delete("/{resource_id}")
async def delete_resource(resource_id: str):
    """Delete a resource."""
    supabase = get_supabase()

    try:
        # Get resource
        resource_response = (
            supabase
            .table("resources")
            .select("*")
            .eq("id", resource_id)
            .execute()
        )

        if not resource_response.data:
            raise HTTPException(
                status_code=404,
                detail="Resource not found"
            )

        resource = resource_response.data[0]

        # Delete file from storage
        if resource.get("file_url"):

            try:
                filename = resource["file_url"].split("/")[-1]

                supabase.storage.from_(
                    "resources"
                ).remove([filename])

            except Exception:
                # Continue even if storage deletion fails
                pass

        # Delete database record
        (
            supabase
            .table("resources")
            .delete()
            .eq("id", resource_id)
            .execute()
        )

        return {
            "message": "Resource deleted successfully"
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )