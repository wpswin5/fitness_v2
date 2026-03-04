-- Create ProgramWorkoutLogs table
-- Version: 019
-- Created: 2026-03-03
-- Description: Tracks completion of each scheduled workout within a program assignment.
--              One row per scheduled workout slot (week/day). Links to WorkoutLogs when completed.
--              Enables progress tracking: completed / total non-rest entries = progress %.

IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'ProgramWorkoutLogs')
BEGIN
    CREATE TABLE [dbo].[ProgramWorkoutLogs] (
        [ProgramWorkoutLogId] UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        [AssignmentId] UNIQUEIDENTIFIER NOT NULL,
        [WeekNumber] INT NOT NULL,
        [DayOfWeek] INT NOT NULL,
        [WorkoutLogId] UNIQUEIDENTIFIER NULL,
        [Status] NVARCHAR(20) NOT NULL DEFAULT 'pending',
        [ScheduledDate] DATE NULL,
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
    PRINT 'ProgramWorkoutLogs table created';
END
ELSE
BEGIN
    PRINT 'ProgramWorkoutLogs table already exists';
END

-- Create indexes (idempotent)
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_ProgramWorkoutLogs_AssignmentId' AND object_id = OBJECT_ID('dbo.ProgramWorkoutLogs'))
    CREATE INDEX [IX_ProgramWorkoutLogs_AssignmentId] ON [dbo].[ProgramWorkoutLogs]([AssignmentId]);

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_ProgramWorkoutLogs_WorkoutLogId' AND object_id = OBJECT_ID('dbo.ProgramWorkoutLogs'))
    CREATE INDEX [IX_ProgramWorkoutLogs_WorkoutLogId] ON [dbo].[ProgramWorkoutLogs]([WorkoutLogId]);

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_ProgramWorkoutLogs_AssignmentId_Status' AND object_id = OBJECT_ID('dbo.ProgramWorkoutLogs'))
    CREATE INDEX [IX_ProgramWorkoutLogs_AssignmentId_Status] ON [dbo].[ProgramWorkoutLogs]([AssignmentId], [Status]);

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_ProgramWorkoutLogs_ScheduledDate' AND object_id = OBJECT_ID('dbo.ProgramWorkoutLogs'))
    CREATE INDEX [IX_ProgramWorkoutLogs_ScheduledDate] ON [dbo].[ProgramWorkoutLogs]([ScheduledDate]);
