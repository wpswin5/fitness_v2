-- ProgramWorkoutLogs Table
-- Tracks completion of each scheduled workout within a program assignment.
-- One row per scheduled workout slot (week/day). Links to WorkoutLogs when completed.
-- Progress = completed / total entries for assignment.

CREATE TABLE [dbo].[ProgramWorkoutLogs] (
    [ProgramWorkoutLogId] UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    [AssignmentId] UNIQUEIDENTIFIER NOT NULL,
    [WeekNumber] INT NOT NULL,
    [DayOfWeek] INT NOT NULL,
    [WorkoutLogId] UNIQUEIDENTIFIER NULL, -- Linked when workout is actually completed
    [Status] NVARCHAR(20) NOT NULL DEFAULT 'pending', -- pending, completed, skipped
    [ScheduledDate] DATE NULL, -- Actual calendar date this was scheduled for
    [CompletedAt] DATETIME2 NULL,
    [Notes] NVARCHAR(MAX),
    [CreatedAt] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    [UpdatedAt] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    CONSTRAINT [FK_ProgramWorkoutLogs_Assignments] FOREIGN KEY ([AssignmentId])
        REFERENCES [dbo].[UserProgramAssignments]([AssignmentId]) ON DELETE CASCADE,
    CONSTRAINT [FK_ProgramWorkoutLogs_WorkoutLogs] FOREIGN KEY ([WorkoutLogId])
        REFERENCES [dbo].[WorkoutLogs]([WorkoutLogId]) ON DELETE NO ACTION,
    CONSTRAINT [CK_ProgramWorkoutLogs_Status] CHECK (
        [Status] IN ('pending', 'completed', 'skipped')
    ),
    CONSTRAINT [CK_ProgramWorkoutLogs_DayOfWeek] CHECK (
        [DayOfWeek] >= 0 AND [DayOfWeek] <= 6
    ),
    CONSTRAINT [UQ_ProgramWorkoutLogs_Slot] UNIQUE ([AssignmentId], [WeekNumber], [DayOfWeek])
);

-- Create indexes
CREATE INDEX [IX_ProgramWorkoutLogs_AssignmentId] ON [dbo].[ProgramWorkoutLogs]([AssignmentId]);
CREATE INDEX [IX_ProgramWorkoutLogs_WorkoutLogId] ON [dbo].[ProgramWorkoutLogs]([WorkoutLogId]);
CREATE INDEX [IX_ProgramWorkoutLogs_AssignmentId_Status] ON [dbo].[ProgramWorkoutLogs]([AssignmentId], [Status]);
CREATE INDEX [IX_ProgramWorkoutLogs_ScheduledDate] ON [dbo].[ProgramWorkoutLogs]([ScheduledDate]);
