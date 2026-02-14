-- Create WorkoutLogs table
-- Version: 012
-- Created: 2026-02-13
-- Description: Top-level record of completed workout sessions

CREATE TABLE [dbo].[WorkoutLogs] (
    [WorkoutLogId] UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    [UserId] UNIQUEIDENTIFIER NOT NULL,
    [OriginalWorkoutId] UNIQUEIDENTIFIER NULL, -- Null for ad-hoc/custom workouts
    [ProgramId] UNIQUEIDENTIFIER NULL, -- If completed as part of a program
    [StartTime] DATETIME2 NOT NULL,
    [EndTime] DATETIME2 NULL, -- Null if workout still in progress
    [TotalDurationMinutes] AS DATEDIFF(MINUTE, [StartTime], [EndTime]) PERSISTED,
    [Notes] NVARCHAR(MAX),
    [CreatedAt] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    CONSTRAINT [FK_WorkoutLogs_Users] FOREIGN KEY ([UserId]) 
        REFERENCES [dbo].[Users]([UserId]) ON DELETE CASCADE,
    CONSTRAINT [FK_WorkoutLogs_Workouts] FOREIGN KEY ([OriginalWorkoutId]) 
        REFERENCES [dbo].[Workouts]([WorkoutId]) ON DELETE NO ACTION,
    CONSTRAINT [FK_WorkoutLogs_Programs] FOREIGN KEY ([ProgramId]) 
        REFERENCES [dbo].[Programs]([ProgramId]) ON DELETE NO ACTION
);

-- Create indexes
CREATE INDEX [IX_WorkoutLogs_UserId] ON [dbo].[WorkoutLogs]([UserId]);
CREATE INDEX [IX_WorkoutLogs_OriginalWorkoutId] ON [dbo].[WorkoutLogs]([OriginalWorkoutId]);
CREATE INDEX [IX_WorkoutLogs_ProgramId] ON [dbo].[WorkoutLogs]([ProgramId]);
CREATE INDEX [IX_WorkoutLogs_StartTime] ON [dbo].[WorkoutLogs]([StartTime] DESC);
CREATE INDEX [IX_WorkoutLogs_UserId_StartTime] ON [dbo].[WorkoutLogs]([UserId], [StartTime] DESC);

PRINT 'WorkoutLogs table created';

