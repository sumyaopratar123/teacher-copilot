-- Row Level Security Policies

-- Enable RLS on all tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE classes ENABLE ROW LEVEL SECURITY;
ALTER TABLE class_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE resources ENABLE ROW LEVEL SECURITY;
ALTER TABLE lesson_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE worksheets ENABLE ROW LEVEL SECURITY;
ALTER TABLE assessments ENABLE ROW LEVEL SECURITY;
ALTER TABLE assessment_questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE assessment_attempts ENABLE ROW LEVEL SECURITY;
ALTER TABLE assessment_answers ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_gaps ENABLE ROW LEVEL SECURITY;
ALTER TABLE remediation_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE remediation_assignments ENABLE ROW LEVEL SECURITY;
ALTER TABLE retests ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE schedules ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_generations ENABLE ROW LEVEL SECURITY;

-- Profiles Policies
-- Users can read their own profile
CREATE POLICY "Users can view own profile"
  ON profiles FOR SELECT
  USING (auth.uid() = id);

-- Users can update their own profile
CREATE POLICY "Users can update own profile"
  ON profiles FOR UPDATE
  USING (auth.uid() = id);

-- Classes Policies
-- Teachers can view their own classes
CREATE POLICY "Teachers can view own classes"
  ON classes FOR SELECT
  USING (
    auth.uid() = teacher_id OR
    id IN (
      SELECT class_id FROM class_members
      WHERE student_id = auth.uid()
    )
  );

-- Teachers can create classes
CREATE POLICY "Teachers can create classes"
  ON classes FOR INSERT
  WITH CHECK (auth.uid() = teacher_id);

-- Teachers can update their own classes
CREATE POLICY "Teachers can update own classes"
  ON classes FOR UPDATE
  USING (auth.uid() = teacher_id);

-- Teachers can delete their own classes
CREATE POLICY "Teachers can delete own classes"
  ON classes FOR DELETE
  USING (auth.uid() = teacher_id);

-- Class Members Policies
-- Students can view their own class memberships
CREATE POLICY "Students can view own memberships"
  ON class_members FOR SELECT
  USING (auth.uid() = student_id);

-- Teachers can view members of their classes
CREATE POLICY "Teachers can view class members"
  ON class_members FOR SELECT
  USING (
    class_id IN (
      SELECT id FROM classes WHERE teacher_id = auth.uid()
    )
  );

-- Students can join classes (via service role or specific function)
CREATE POLICY "Anyone can join classes"
  ON class_members FOR INSERT
  WITH CHECK (true);

-- Teachers can remove students from their classes
CREATE POLICY "Teachers can remove students"
  ON class_members FOR DELETE
  USING (
    class_id IN (
      SELECT id FROM classes WHERE teacher_id = auth.uid()
    )
  );

-- Resources Policies
-- Teachers can view resources in their classes
CREATE POLICY "Teachers can view class resources"
  ON resources FOR SELECT
  USING (
    class_id IN (
      SELECT id FROM classes WHERE teacher_id = auth.uid()
    )
  );

-- Students can view resources in their classes
CREATE POLICY "Students can view class resources"
  ON resources FOR SELECT
  USING (
    class_id IN (
      SELECT class_id FROM class_members WHERE student_id = auth.uid()
    )
  );

-- Teachers can create resources in their classes
CREATE POLICY "Teachers can create resources"
  ON resources FOR INSERT
  WITH CHECK (
    auth.uid() = uploader_id AND
    class_id IN (
      SELECT id FROM classes WHERE teacher_id = auth.uid()
    )
  );

-- Lesson Plans Policies
-- Teachers can view their own lesson plans
CREATE POLICY "Teachers can view own lesson plans"
  ON lesson_plans FOR SELECT
  USING (auth.uid() = teacher_id);

-- Teachers can create lesson plans
CREATE POLICY "Teachers can create lesson plans"
  ON lesson_plans FOR INSERT
  WITH CHECK (auth.uid() = teacher_id);

-- Teachers can update their own lesson plans
CREATE POLICY "Teachers can update own lesson plans"
  ON lesson_plans FOR UPDATE
  USING (auth.uid() = teacher_id);

-- Worksheets Policies
-- Teachers can view their own worksheets
CREATE POLICY "Teachers can view own worksheets"
  ON worksheets FOR SELECT
  USING (auth.uid() = teacher_id);

-- Teachers can create worksheets
CREATE POLICY "Teachers can create worksheets"
  ON worksheets FOR INSERT
  WITH CHECK (auth.uid() = teacher_id);

-- Assessments Policies
-- Teachers can view assessments in their classes
CREATE POLICY "Teachers can view class assessments"
  ON assessments FOR SELECT
  USING (
    auth.uid() = teacher_id OR
    class_id IN (
      SELECT class_id FROM class_members WHERE student_id = auth.uid()
    )
  );

-- Teachers can create assessments in their classes
CREATE POLICY "Teachers can create assessments"
  ON assessments FOR INSERT
  WITH CHECK (
    auth.uid() = teacher_id AND
    class_id IN (
      SELECT id FROM classes WHERE teacher_id = auth.uid()
    )
  );

-- Teachers can update their own assessments
CREATE POLICY "Teachers can update own assessments"
  ON assessments FOR UPDATE
  USING (auth.uid() = teacher_id);

-- Assessment Questions Policies
-- Teachers can view questions in their assessments
CREATE POLICY "Teachers can view assessment questions"
  ON assessment_questions FOR SELECT
  USING (
    assessment_id IN (
      SELECT id FROM assessments WHERE teacher_id = auth.uid()
    )
  );

-- Students can view questions in their class assessments
CREATE POLICY "Students can view assessment questions"
  ON assessment_questions FOR SELECT
  USING (
    assessment_id IN (
      SELECT id FROM assessments 
      WHERE class_id IN (
        SELECT class_id FROM class_members WHERE student_id = auth.uid()
      )
    )
  );

-- Assessment Attempts Policies
-- Students can view their own attempts
CREATE POLICY "Students can view own attempts"
  ON assessment_attempts FOR SELECT
  USING (auth.uid() = student_id);

-- Teachers can view attempts in their classes
CREATE POLICY "Teachers can view class attempts"
  ON assessment_attempts FOR SELECT
  USING (
    assessment_id IN (
      SELECT id FROM assessments WHERE teacher_id = auth.uid()
    )
  );

-- Students can create attempts
CREATE POLICY "Students can create attempts"
  ON assessment_attempts FOR INSERT
  WITH CHECK (auth.uid() = student_id);

-- Assessment Answers Policies
-- Students can view their own answers
CREATE POLICY "Students can view own answers"
  ON assessment_answers FOR SELECT
  USING (
    attempt_id IN (
      SELECT id FROM assessment_attempts WHERE student_id = auth.uid()
    )
  );

-- Students can create answers
CREATE POLICY "Students can create answers"
  ON assessment_answers FOR INSERT
  WITH CHECK (
    attempt_id IN (
      SELECT id FROM assessment_attempts WHERE student_id = auth.uid()
    )
  );

-- Learning Gaps Policies
-- Students can view their own learning gaps
CREATE POLICY "Students can view own learning gaps"
  ON learning_gaps FOR SELECT
  USING (auth.uid() = student_id);

-- Teachers can view learning gaps in their classes
CREATE POLICY "Teachers can view class learning gaps"
  ON learning_gaps FOR SELECT
  USING (
    student_id IN (
      SELECT student_id FROM class_members
      WHERE class_id IN (
        SELECT id FROM classes WHERE teacher_id = auth.uid()
      )
    )
  );

-- Remediation Plans Policies
-- Teachers can view their own remediation plans
CREATE POLICY "Teachers can view own remediation plans"
  ON remediation_plans FOR SELECT
  USING (auth.uid() = teacher_id);

-- Teachers can create remediation plans
CREATE POLICY "Teachers can create remediation plans"
  ON remediation_plans FOR INSERT
  WITH CHECK (auth.uid() = teacher_id);

-- Remediation Assignments Policies
-- Students can view their own remediation assignments
CREATE POLICY "Students can view own remediation assignments"
  ON remediation_assignments FOR SELECT
  USING (auth.uid() = student_id);

-- Teachers can view remediation assignments in their classes
CREATE POLICY "Teachers can view class remediation assignments"
  ON remediation_assignments FOR SELECT
  USING (
    student_id IN (
      SELECT student_id FROM class_members
      WHERE class_id IN (
        SELECT id FROM classes WHERE teacher_id = auth.uid()
      )
    )
  );

-- Students can update their own remediation assignments
CREATE POLICY "Students can update own remediation assignments"
  ON remediation_assignments FOR UPDATE
  USING (auth.uid() = student_id);

-- Retests Policies
-- Students can view their own retests
CREATE POLICY "Students can view own retests"
  ON retests FOR SELECT
  USING (auth.uid() = student_id);

-- Teachers can view retests in their classes
CREATE POLICY "Teachers can view class retests"
  ON retests FOR SELECT
  USING (
    student_id IN (
      SELECT student_id FROM class_members
      WHERE class_id IN (
        SELECT id FROM classes WHERE teacher_id = auth.uid()
      )
    )
  );

-- Student Progress Policies
-- Students can view their own progress
CREATE POLICY "Students can view own progress"
  ON student_progress FOR SELECT
  USING (auth.uid() = student_id);

-- Teachers can view progress in their classes
CREATE POLICY "Teachers can view class progress"
  ON student_progress FOR SELECT
  USING (
    student_id IN (
      SELECT student_id FROM class_members
      WHERE class_id IN (
        SELECT id FROM classes WHERE teacher_id = auth.uid()
      )
    )
  );

-- Schedules Policies
-- Teachers can view their own schedules
CREATE POLICY "Teachers can view own schedules"
  ON schedules FOR SELECT
  USING (auth.uid() = teacher_id);

-- Students can view schedules in their classes
CREATE POLICY "Students can view class schedules"
  ON schedules FOR SELECT
  USING (
    class_id IN (
      SELECT class_id FROM class_members WHERE student_id = auth.uid()
    )
  );

-- Teachers can create schedules
CREATE POLICY "Teachers can create schedules"
  ON schedules FOR INSERT
  WITH CHECK (auth.uid() = teacher_id);

-- Notifications Policies
-- Users can view their own notifications
CREATE POLICY "Users can view own notifications"
  ON notifications FOR SELECT
  USING (auth.uid() = user_id);

-- Users can update their own notifications
CREATE POLICY "Users can update own notifications"
  ON notifications FOR UPDATE
  USING (auth.uid() = user_id);

-- AI Generations Policies
-- Users can view their own AI generations
CREATE POLICY "Users can view own AI generations"
  ON ai_generations FOR SELECT
  USING (auth.uid() = user_id);

-- Users can create AI generations
CREATE POLICY "Users can create AI generations"
  ON ai_generations FOR INSERT
  WITH CHECK (auth.uid() = user_id);
