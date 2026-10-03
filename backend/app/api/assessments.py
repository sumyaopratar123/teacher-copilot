from fastapi import APIRouter, HTTPException, status
from typing import List
from app.core.supabase_client import get_supabase
from app.models.assessment import (
    AssessmentCreate, Assessment, AssessmentAttemptCreate, 
    AssessmentAttempt, AnswerSubmit
)

router = APIRouter(prefix="/assessments", tags=["assessments"])


@router.post("", response_model=Assessment)
async def create_assessment(assessment_data: AssessmentCreate, teacher_id: str):
    """Create a new assessment"""
    supabase = get_supabase()
    
    try:
        # Verify teacher exists
        profile_response = supabase.table("profiles").select("*").eq("id", teacher_id).eq("role", "teacher").execute()
        
        if not profile_response.data:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only teachers can create assessments"
            )
        
        # Create assessment
        assessment_insert = {
            "teacher_id": teacher_id,
            "class_id": assessment_data.class_id,
            "title": assessment_data.title,
            "type": assessment_data.type,
            "subject": assessment_data.subject,
            "topic": assessment_data.topic,
            "duration": assessment_data.duration,
            "total_marks": assessment_data.total_marks,
            "passing_score": assessment_data.passing_score,
            "start_date": assessment_data.start_date.isoformat() if assessment_data.start_date else None,
            "due_date": assessment_data.due_date.isoformat() if assessment_data.due_date else None,
            "instructions": assessment_data.instructions
        }
        
        assessment_response = supabase.table("assessments").insert(assessment_insert).execute()
        
        if not assessment_response.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create assessment"
            )
        
        assessment_id = assessment_response.data[0]["id"]
        
        # Create questions
        questions_data = []
        for i, question in enumerate(assessment_data.questions):
            question_insert = {
                "assessment_id": assessment_id,
                "question_text": question.question_text,
                "question_type": question.question_type,
                "options": question.options,
                "correct_answer": question.correct_answer,
                "marks": question.marks,
                "difficulty": question.difficulty,
                "topic": question.topic,
                "order_index": question.order_index
            }
            questions_data.append(question_insert)
        
        questions_response = supabase.table("assessment_questions").insert(questions_data).execute()
        
        # Return assessment with questions
        final_response = supabase.table("assessments").select("*").eq("id", assessment_id).execute()
        return final_response.data[0]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("")
async def get_assessments(class_id: str = None, teacher_id: str = None):
    """Get assessments for a class or teacher"""
    supabase = get_supabase()
    
    try:
        if class_id:
            response = supabase.table("assessments").select("*").eq("class_id", class_id).execute()
        elif teacher_id:
            response = supabase.table("assessments").select("*").eq("teacher_id", teacher_id).execute()
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Must provide class_id or teacher_id"
            )
        
        return response.data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{assessment_id}", response_model=Assessment)
async def get_assessment(assessment_id: str):
    """Get a specific assessment with questions"""
    supabase = get_supabase()
    
    try:
        response = supabase.table("assessments").select("*").eq("id", assessment_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment not found"
            )
        
        # Get questions
        questions_response = supabase.table("assessment_questions").select("*").eq("assessment_id", assessment_id).order("order_index").execute()
        
        assessment = response.data[0]
        assessment["questions"] = questions_response.data
        
        return assessment
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{assessment_id}/start", response_model=AssessmentAttempt)
async def start_assessment(assessment_id: str, student_id: str):
    """Start an assessment (create attempt)"""
    supabase = get_supabase()
    
    try:
        # Verify student exists
        profile_response = supabase.table("profiles").select("*").eq("id", student_id).eq("role", "student").execute()
        
        if not profile_response.data:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only students can start assessments"
            )
        
        # Check if already started
        existing = supabase.table("assessment_attempts").select("*").eq("assessment_id", assessment_id).eq("student_id", student_id).execute()
        
        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assessment already started"
            )
        
        # Create attempt
        attempt_insert = {
            "assessment_id": assessment_id,
            "student_id": student_id
        }
        
        response = supabase.table("assessment_attempts").insert(attempt_insert).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to start assessment"
            )
        
        return response.data[0]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{assessment_id}/submit")
async def submit_assessment(assessment_id: str, student_id: str, answers: List[AnswerSubmit]):
    """Submit an assessment"""
    supabase = get_supabase()
    
    try:
        # Get attempt
        attempt_response = supabase.table("assessment_attempts").select("*").eq("assessment_id", assessment_id).eq("student_id", student_id).execute()
        
        if not attempt_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment attempt not found"
            )
        
        attempt = attempt_response.data[0]
        
        if attempt.get("submitted_at"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assessment already submitted"
            )
        
        # Get questions
        questions_response = supabase.table("assessment_questions").select("*").eq("assessment_id", assessment_id).execute()
        questions = {q["id"]: q for q in questions_response.data}
        
        # Calculate score
        total_marks = 0
        obtained_marks = 0
        
        # Save answers
        answer_records = []
        for answer in answers:
            question = questions.get(answer.question_id)
            if question:
                total_marks += question["marks"]
                is_correct = answer.answer == question["correct_answer"]
                if is_correct:
                    obtained_marks += question["marks"]
                
                answer_records.append({
                    "attempt_id": attempt["id"],
                    "question_id": answer.question_id,
                    "answer": answer.answer,
                    "is_correct": is_correct,
                    "marks_obtained": question["marks"] if is_correct else 0
                })
        
        # Insert answers
        supabase.table("assessment_answers").insert(answer_records).execute()
        
        # Update attempt
        percentage = (obtained_marks / total_marks * 100) if total_marks > 0 else 0
        update_data = {
            "submitted_at": "now()",
            "score": obtained_marks,
            "total_marks": total_marks,
            "percentage": percentage,
            "passed": percentage >= 50  # Default passing threshold
        }
        
        supabase.table("assessment_attempts").update(update_data).eq("id", attempt["id"]).execute()
        
        # Trigger learning gap detection
        try:
            gap_response = supabase.table("learning_gaps").select("*").eq(
                "student_id", student_id
            ).eq("assessment_id", assessment_id).is_("resolved_at", None).execute()
            
            if not gap_response.data:
                # Detect learning gaps
                topic_performance = {}
                for answer in answers:
                    question = questions.get(answer.question_id)
                    if question:
                        topic = question.get("topic", "topic")
                        if topic not in topic_performance:
                            topic_performance[topic] = {"correct": 0, "total": 0}
                        topic_performance[topic]["total"] += 1
                        if answer.answer == question["correct_answer"]:
                            topic_performance[topic]["correct"] += 1
                
                for topic, perf in topic_performance.items():
                    topic_percent = (perf["correct"] / perf["total"] * 100) if perf["total"] > 0 else 0
                    if topic_percent < 50:
                        assessment_data = supabase.table("assessments").select("*").eq("id", assessment_id).execute()
                        if assessment_data.data:
                            supabase.table("learning_gaps").insert({
                                "student_id": student_id,
                                "assessment_id": assessment_id,
                                "topic": topic,
                                "subject": assessment_data.data[0]["subject"],
                                "confidence": "high" if topic_percent < 30 else "medium",
                                "reason": f"Scored {topic_percent:.0f}% on {topic}",
                                "current_level": "foundation" if topic_percent < 30 else "developing"
                            }).execute()
        except Exception as e:
            print(f"Learning gap detection failed: {e}")
        
        return {
            "message": "Assessment submitted successfully",
            "score": obtained_marks,
            "total_marks": total_marks,
            "percentage": percentage,
            "passed": percentage >= 50
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{assessment_id}/attempts")
async def get_assessment_attempts(assessment_id: str, teacher_id: str = None):
    """Get all attempts for an assessment (teacher only)"""
    supabase = get_supabase()
    
    try:
        if teacher_id:
            # Verify teacher owns the assessment
            assessment_response = supabase.table("assessments").select("*").eq("id", assessment_id).eq("teacher_id", teacher_id).execute()
            
            if not assessment_response.data:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only view attempts for your own assessments"
                )
        
        response = supabase.table("assessment_attempts").select("*, profiles(*)").eq("assessment_id", assessment_id).execute()
        
        return response.data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/student/{student_id}")
async def get_student_assessments(student_id: str):
    """Get all assessments for a student"""
    supabase = get_supabase()
    
    try:
        response = supabase.table("assessment_attempts").select("*, assessments(*)").eq("student_id", student_id).execute()
        
        return response.data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
