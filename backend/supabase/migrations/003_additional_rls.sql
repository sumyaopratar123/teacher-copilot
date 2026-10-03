-- Additional RLS policies for new features

-- Allow service role for seed data and admin operations
-- This is for development purposes, remove in production
CREATE POLICY "Service role bypass" ON ALL TABLES
  FOR ALL
  USING (auth.role() = 'service_role');

-- Learning Gaps
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

-- Remediation Plans
CREATE POLICY "Teachers can view remediation plans"
  ON remediation_plans FOR SELECT
  USING (auth.uid() = teacher_id);

CREATE POLICY "Students can view assigned remediation"
  ON remediation_plans FOR SELECT
  USING (
    id IN (
      SELECT remediation_plan_id FROM remediation_assignments
      WHERE student_id = auth.uid()
    )
  );

-- Remediation Assignments
CREATE POLICY "Students can view own assignments"
  ON remediation_assignments FOR SELECT
  USING (auth.uid() = student_id);

CREATE POLICY "Teachers can view class assignments"
  ON remediation_assignments FOR SELECT
  USING (
    student_id IN (
      SELECT student_id FROM class_members
      WHERE class_id IN (
        SELECT id FROM classes WHERE teacher_id = auth.uid()
      )
    )
  );

CREATE POLICY "Students can update own assignments"
  ON remediation_assignments FOR UPDATE
  USING (auth.uid() = student_id);

-- Retests
CREATE POLICY "Students can view own retests"
  ON retests FOR SELECT
  USING (auth.uid() = student_id);

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

-- Student Progress
CREATE POLICY "Students can view own progress"
  ON student_progress FOR SELECT
  USING (auth.uid() = student_id);

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

-- Resources
CREATE POLICY "Teachers can upload to own classes"
  ON resources FOR INSERT
  WITH CHECK (
    auth.uid() = uploader_id AND
    class_id IN (
      SELECT id FROM classes WHERE teacher_id = auth.uid()
    )
  );

CREATE POLICY "Students can upload to enrolled classes"
  ON resources FOR INSERT
  WITH CHECK (
    auth.uid() = uploader_id AND
    class_id IN (
      SELECT class_id FROM class_members WHERE student_id = auth.uid()
    )
  );

CREATE POLICY "Users can delete own resources"
  ON resources FOR DELETE
  USING (auth.uid() = uploader_id);

-- Notifications
CREATE POLICY "Users can create notifications for themselves"
  ON notifications FOR INSERT
  WITH CHECK (auth.uid() = user_id);
