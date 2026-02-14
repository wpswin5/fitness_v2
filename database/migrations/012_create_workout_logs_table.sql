-- Create WorkoutLogs table
-- Version: 012
-- Created: 2026-02-13
-- Description: Top-level record of completed workout sessions

IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'WorkoutLogs')
BEGIN
    CREATE TABLE [dbo].[WorkoutLogs] (
        [WorkoutLogId] UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        [UserId] UNIQUEIDENTIFIER NOT NULL,
        [OriginalWorkoutId] UNIQUEIDENTIFIER NULL,
        [ProgramId] UNIQUEIDENTIFIER NULL,
        [StartTime] DATETIME2 NOT NULL,
        [EndTime] DATETIME2 NULL,
        [TotalDurationMinutes] AS DATEDIFF(MINUTE, [StartTime], [EndTime]),
        [Notes] NVARCHAR(MAX),
        [CreatedAt] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        CONSTRAINT [FK_WorkoutLogs_Users] FOREIGN KEY ([UserId]) 
            REFERENCES [dbo].[Users]([UserId]) ON DELETE CASCADE,
        CONSTRAINT [FK_WorkoutLogs_Workouts] FOREIGN KEY ([OriginalWorkoutId]) 
            REFERENCES [dbo].[Workouts]([WorkoutId]) ON DELETE NO ACTION,
        CONSTRAINT [FK_WorkoutLogs_Programs] FOREIGN KEY ([ProgramId]) 
            REFERENCES [dbo].[Programs]([ProgramId]) ON DELETE NO ACTION
    );
    PRINT 'WorkoutLogs table created';
END
ELSE
BEGIN
    PRINT 'WorkoutLogs table already exists';
END

-- Create indexes (idempotent)
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_WorkoutLogs_UserId' AND object_id = OBJECT_ID('dbo.WorkoutLogs'))
    CREATE INDEX [IX_WorkoutLogs_UserId] ON [dbo].[WorkoutLogs]([UserId]);

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_WorkoutLogs_OriginalWorkoutId' AND object_id = OBJECT_ID('dbo.WorkoutLogs'))
    CREATE INDEX [IX_WorkoutLogs_OriginalWorkoutId] ON [dbo].[WorkoutLogs]([OriginalWorkoutId]);

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_WorkoutLogs_ProgramId' AND object_id = OBJECT_ID('dbo.WorkoutLogs'))
    CREATE INDEX [IX_WorkoutLogs_ProgramId] ON [dbo].[WorkoutLogs]([ProgramId]);

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_WorkoutLogs_StartTime' AND object_id = OBJECT_ID('dbo.WorkoutLogs'))
    CREATE INDEX [IX_WorkoutLogs_StartTime] ON [dbo].[WorkoutLogs]([StartTime] DESC);

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_WorkoutLogs_UserId_StartTime' AND object_id = OBJECT_ID('dbo.WorkoutLogs'))
    CREATE INDEX [IX_WorkoutLogs_UserId_StartTime] ON [dbo].[WorkoutLogs]([UserId], [StartTime] DESC);

