from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Optional
import random
import string

from app.core.supabase_client import get_supabase
from app.models.class_models import ClassCreate, ClassUpdate, Class, ClassMember


router = APIRouter(prefix="/classes", tags=["classes"])


def generate_class_code():
    """Generate a unique 6-character class code"""
    return ''.join(
        random.choices(
            string.ascii_uppercase + string.digits,
            k=6
        )
    )


@router.post("", response_model=Class)
async def create_class(class_data: ClassCreate, teacher_id: str):
    """Create a new class"""
    supabase = get_supabase()

    try:
        # Verify teacher exists and has teacher role
        profile_response = (
            supabase
            .table("profiles")
            .select("*")
            .eq("id", teacher_id)
            .eq("role", "teacher")
            .execute()
        )

        if not profile_response.data:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only teachers can create classes"
            )

        # Check if class code already exists
        existing = (
            supabase
            .table("classes")
            .select("*")
            .eq("class_code", class_data.class_code)
            .execute()
        )

        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Class code already exists"
            )

        # Create class
        class_insert = {
            "teacher_id": teacher_id,
            "name": class_data.name,
            "grade": class_data.grade,
            "subject": class_data.subject,
            "section": class_data.section,
            "academic_year": class_data.academic_year,
            "description": class_data.description,
            "class_code": class_data.class_code
        }

        response = (
            supabase
            .table("classes")
            .insert(class_insert)
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create class"
            )

        return response.data[0]

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("")
async def get_classes(
    teacher_id: Optional[str] = None,
    student_id: Optional[str] = None
):
    """Get classes for a teacher or student"""
    supabase = get_supabase()

    try:
        if teacher_id:
            # Get classes taught by teacher
            response = (
                supabase
                .table("classes")
                .select("*")
                .eq("teacher_id", teacher_id)
                .execute()
            )

            return response.data

        elif student_id:
            # Get classes student is enrolled in
            response = (
                supabase
                .table("class_members")
                .select("classes(*)")
                .eq("student_id", student_id)
                .execute()
            )

            # Extract classes from nested structure
            classes = [
                item["classes"]
                for item in response.data
                if item.get("classes")
            ]

            return classes

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Must provide teacher_id or student_id"
            )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{class_id}", response_model=Class)
async def get_class(class_id: str):
    """Get a specific class"""
    supabase = get_supabase()

    try:
        response = (
            supabase
            .table("classes")
            .select("*")
            .eq("id", class_id)
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Class not found"
            )

        return response.data[0]

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{class_id}", response_model=Class)
async def update_class(
    class_id: str,
    class_data: ClassUpdate,
    teacher_id: str
):
    """Update a class"""
    supabase = get_supabase()

    try:
        # Verify teacher owns the class
        class_response = (
            supabase
            .table("classes")
            .select("*")
            .eq("id", class_id)
            .eq("teacher_id", teacher_id)
            .execute()
        )

        if not class_response.data:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own classes"
            )

        # Update class
        update_data = {
            k: v
            for k, v in class_data.model_dump().items()
            if v is not None
        }

        response = (
            supabase
            .table("classes")
            .update(update_data)
            .eq("id", class_id)
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create class"
            )

        return response.data[0]

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{class_id}")
async def delete_class(class_id: str, teacher_id: str):
    """Delete a class"""
    supabase = get_supabase()

    try:
        # Verify teacher owns the class
        class_response = (
            supabase
            .table("classes")
            .select("*")
            .eq("id", class_id)
            .eq("teacher_id", teacher_id)
            .execute()
        )

        if not class_response.data:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own classes"
            )

        # Delete class
        response = (
            supabase
            .table("classes")
            .delete()
            .eq("id", class_id)
            .execute()
        )

        return {
            "message": "Class deleted successfully"
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{class_id}/join")
async def join_class(class_id: str, student_id: str):
    """Student joins a class by class ID"""
    supabase = get_supabase()

    try:
        # Verify student exists
        profile_response = (
            supabase
            .table("profiles")
            .select("*")
            .eq("id", student_id)
            .eq("role", "student")
            .execute()
        )

        if not profile_response.data:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only students can join classes"
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
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Class not found"
            )

        # Check if already a member
        existing = (
            supabase
            .table("class_members")
            .select("*")
            .eq("class_id", class_id)
            .eq("student_id", student_id)
            .execute()
        )

        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Already a member of this class"
            )

        # Add student to class
        response = (
            supabase
            .table("class_members")
            .insert({
                "class_id": class_id,
                "student_id": student_id
            })
            .execute()
        )

        return {
            "message": f"Successfully joined {class_response.data[0]['name']}",
            "class": class_response.data[0]
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/join-by-code")
async def join_class_by_code(
    class_code: str,
    student_id: str
):
    """Student joins a class by class code"""
    supabase = get_supabase()

    try:
        # Find class by code
        class_response = (
            supabase
            .table("classes")
            .select("*")
            .eq("class_code", class_code)
            .execute()
        )

        if not class_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid class code"
            )

        class_id = class_response.data[0]["id"]

        return await join_class(
            class_id,
            student_id
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{class_id}/students")
async def get_class_students(
    class_id: str,
    teacher_id: str
):
    """Get all students in a class"""
    supabase = get_supabase()

    try:
        # Verify teacher owns the class
        class_response = (
            supabase
            .table("classes")
            .select("*")
            .eq("id", class_id)
            .eq("teacher_id", teacher_id)
            .execute()
        )

        if not class_response.data:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view students in your own classes"
            )

        # Get students
        response = (
            supabase
            .table("class_members")
            .select("profiles(*), joined_at")
            .eq("class_id", class_id)
            .execute()
        )

        students = []

        for item in response.data:
            if item.get("profiles"):
                students.append({
                    **item["profiles"],
                    "joined_at": item["joined_at"]
                })

        return students

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{class_id}/students/{student_id}")
async def remove_student(
    class_id: str,
    student_id: str,
    teacher_id: str
):
    """Remove a student from a class"""
    supabase = get_supabase()

    try:
        # Verify teacher owns the class
        class_response = (
            supabase
            .table("classes")
            .select("*")
            .eq("id", class_id)
            .eq("teacher_id", teacher_id)
            .execute()
        )

        if not class_response.data:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only remove students from your own classes"
            )

        # Remove student
        response = (
            supabase
            .table("class_members")
            .delete()
            .eq("class_id", class_id)
            .eq("student_id", student_id)
            .execute()
        )

        return {
            "message": "Student removed successfully"
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )