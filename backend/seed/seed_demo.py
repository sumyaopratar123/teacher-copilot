"""
Seed script for Teacher Copilot demo data.

This script creates:
- 1 Teacher
- 3 Students
- 1 Class
- 3 Assessments
- Student attempts
- Learning gaps
- Remediation plans

Run this script after setting up Supabase to have demo data for testing.
"""

import os
from supabase import create_client
from dotenv import load_dotenv
import random
import string

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    print("Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in .env")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


def generate_class_code():
    """Generate a 6-character class code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


def clear_existing_data():
    """Clear existing demo data"""
    print("Clearing existing data...")
    
    # Delete in order of dependencies
    supabase.table("ai_generations").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    supabase.table("notifications").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    supabase.table("schedules").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    supabase.table("student_progress").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    supabase.table("retests").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    supabase.table("remediation_assignments").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    supabase.table("remediation_plans").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    supabase.table("learning_gaps").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    supabase.table("assessment_answers").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    supabase.table("assessment_attempts").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    supabase.table("assessment_questions").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    supabase.table("assessments").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    supabase.table("class_members").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    supabase.table("classes").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    supabase.table("profiles").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    
    print("Existing data cleared.")


def seed_users():
    """Create teacher and student users"""
    print("Creating users...")
    
    # Create teacher
    teacher_email = "teacher@demo.com"
    teacher_password = "demo123"
    
    teacher_auth = supabase.auth.sign_up({
        "email": teacher_email,
        "password": teacher_password,
        "options": {
            "data": {
                "full_name": "Demo Teacher",
                "role": "teacher"
            }
        }
    })
    
    if teacher_auth.user:
        teacher_id = teacher_auth.user.id
        print(f"Created teacher: {teacher_email} / {teacher_password}")
    else:
        print("Error creating teacher")
        return None, []
    
    # Create teacher profile
    supabase.table("profiles").insert({
        "id": teacher_id,
        "email": teacher_email,
        "full_name": "Demo Teacher",
        "role": "teacher"
    }).execute()
    
    # Create students
    students = []
    student_data = [
        {"name": "Alice Johnson", "email": "alice@demo.com"},
        {"name": "Bob Smith", "email": "bob@demo.com"},
        {"name": "Charlie Brown", "email": "charlie@demo.com"},
    ]
    
    for i, student in enumerate(student_data):
        student_password = "demo123"
        student_auth = supabase.auth.sign_up({
            "email": student["email"],
            "password": student_password,
            "options": {
                "data": {
                    "full_name": student["name"],
                    "role": "student"
                }
            }
        })
        
        if student_auth.user:
            student_id = student_auth.user.id
            supabase.table("profiles").insert({
                "id": student_id,
                "email": student["email"],
                "full_name": student["name"],
                "role": "student"
            }).execute()
            
            students.append({
                "id": student_id,
                "email": student["email"],
                "name": student["name"],
                "password": student_password
            })
            print(f"Created student: {student['email']} / {student_password}")
    
    return teacher_id, students


def seed_class(teacher_id):
    """Create a demo class"""
    print("Creating class...")
    
    class_code = generate_class_code()
    
    class_data = {
        "teacher_id": teacher_id,
        "name": "8-A Mathematics",
        "grade": "8",
        "subject": "Mathematics",
        "section": "A",
        "academic_year": "2024-2025",
        "description": "Grade 8 Mathematics - Section A",
        "class_code": class_code
    }
    
    result = supabase.table("classes").insert(class_data).execute()
    
    if result.data:
        class_id = result.data[0]["id"]
        print(f"Created class: 8-A Mathematics (Code: {class_code})")
        return class_id, class_code
    else:
        print("Error creating class")
        return None, None


def seed_class_members(class_id, students):
    """Enroll students in the class"""
    print("Enrolling students...")
    
    for student in students:
        supabase.table("class_members").insert({
            "class_id": class_id,
            "student_id": student["id"]
        }).execute()
        print(f"Enrolled {student['name']} in class")


def seed_assessments(teacher_id, class_id):
    """Create demo assessments"""
    print("Creating assessments...")
    
    assessments = []
    topics = ["Fractions", "Decimals", "Linear Equations"]
    
    for i, topic in enumerate(topics):
        assessment_data = {
            "teacher_id": teacher_id,
            "class_id": class_id,
            "title": f"{topic} Quiz",
            "type": "quiz",
            "subject": "Mathematics",
            "topic": topic,
            "duration": 30,
            "total_marks": 10,
            "passing_score": 6,
            "instructions": f"Answer all questions about {topic}"
        }
        
        result = supabase.table("assessments").insert(assessment_data).execute()
        
        if result.data:
            assessment_id = result.data[0]["id"]
            assessments.append({"id": assessment_id, "topic": topic})
            
            # Add questions
            for j in range(5):
                question_data = {
                    "assessment_id": assessment_id,
                    "question_text": f"Question {j+1} about {topic}",
                    "question_type": "mcq",
                    "options": ["A", "B", "C", "D"],
                    "correct_answer": "A",
                    "marks": 2,
                    "difficulty": "developing",
                    "topic": topic,
                    "order_index": j
                }
                supabase.table("assessment_questions").insert(question_data).execute()
            
            print(f"Created assessment: {topic} Quiz")
    
    return assessments


def seed_assessment_attempts(assessments, students):
    """Create student assessment attempts with varying scores"""
    print("Creating assessment attempts...")
    
    for assessment in assessments:
        for student in students:
            # Simulate different performance levels
            if assessment["topic"] == "Linear Equations":
                # Poor performance for Linear Equations (to demonstrate learning gap)
                score = 4
            else:
                # Good performance for other topics
                score = random.randint(7, 10)
            
            attempt_data = {
                "assessment_id": assessment["id"],
                "student_id": student["id"],
                "submitted_at": "now()",
                "score": score,
                "total_marks": 10,
                "percentage": score * 10,
                "passed": score >= 6,
                "time_taken": random.randint(15, 30)
            }
            
            result = supabase.table("assessment_attempts").insert(attempt_data).execute()
            
            if result.data:
                attempt_id = result.data[0]["id"]
                print(f"Created attempt for {student['name']} on {assessment['topic']}: {score}/10")


def seed_learning_gaps(students, assessments):
    """Create learning gaps for poor performance"""
    print("Creating learning gaps...")
    
    linear_equations_assessment = next(a for a in assessments if a["topic"] == "Linear Equations")
    
    for student in students:
        gap_data = {
            "student_id": student["id"],
            "assessment_id": linear_equations_assessment["id"],
            "topic": "Linear Equations",
            "subject": "Mathematics",
            "confidence": "high",
            "reason": "Student scored below passing threshold on Linear Equations quiz",
            "current_level": "foundation"
        }
        
        result = supabase.table("learning_gaps").insert(gap_data).execute()
        
        if result.data:
            gap_id = result.data[0]["id"]
            print(f"Created learning gap for {student['name']}: Linear Equations")


def seed_remediation(teacher_id, learning_gaps):
    """Create remediation plans"""
    print("Creating remediation plans...")
    
    # Get learning gaps
    gaps_result = supabase.table("learning_gaps").select("*").execute()
    gaps = gaps_result.data
    
    for gap in gaps:
        remediation_data = {
            "learning_gap_id": gap["id"],
            "teacher_id": teacher_id,
            "title": f"Remediation for {gap['topic']}",
            "content": {
                "simplified_explanation": f"Basic explanation of {gap['topic']}",
                "worked_examples": ["Example 1", "Example 2"],
                "practice_questions": ["Practice question 1", "Practice question 2"]
            },
            "target_level": "developing",
            "teacher_approved": True
        }
        
        result = supabase.table("remediation_plans").insert(remediation_data).execute()
        
        if result.data:
            print(f"Created remediation plan for {gap['topic']}")


def main():
    print("=" * 50)
    print("Teacher Copilot - Demo Data Seed Script")
    print("=" * 50)
    print()
    
    # Clear existing data
    clear_existing_data()
    print()
    
    # Seed users
    teacher_id, students = seed_users()
    if not teacher_id:
        print("Failed to create users. Exiting.")
        return
    
    print()
    
    # Seed class
    class_id, class_code = seed_class(teacher_id)
    if not class_id:
        print("Failed to create class. Exiting.")
        return
    
    print()
    
    # Enroll students
    seed_class_members(class_id, students)
    print()
    
    # Seed assessments
    assessments = seed_assessments(teacher_id, class_id)
    print()
    
    # Seed assessment attempts
    seed_assessment_attempts(assessments, students)
    print()
    
    # Seed learning gaps
    seed_learning_gaps(students, assessments)
    print()
    
    # Seed remediation
    seed_remediation(teacher_id, None)
    print()
    
    print("=" * 50)
    print("Demo data seeded successfully!")
    print("=" * 50)
    print()
    print("Login Credentials:")
    print(f"Teacher: teacher@demo.com / demo123")
    print(f"Student 1: alice@demo.com / demo123")
    print(f"Student 2: bob@demo.com / demo123")
    print(f"Student 3: charlie@demo.com / demo123")
    print()
    print(f"Class Code: {class_code}")
    print()
    print("Use these credentials to test the application.")


if __name__ == "__main__":
    main()
