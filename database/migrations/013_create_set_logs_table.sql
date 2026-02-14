-- Create SetLogs table
-- Version: 013
-- Created: 2026-02-13
-- Description: Individual execution of a set during a workout

CREATE TABLE [dbo].[SetLogs] (
    [SetLogId] UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    [WorkoutLogId] UNIQUEIDENTIFIER NOT NULL,
    [OriginalSetId] UNIQUEIDENTIFIER NULL, -- Null for ad-hoc sets
    [SetOrder] INT NOT NULL, -- Order of the exercise in the workout
    [ExerciseId] UNIQUEIDENTIFIER NOT NULL,
    [SetNumber] INT NOT NULL, -- Which occurrence (1st, 2nd, 3rd of num_sets)
    [CreatedAt] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    CONSTRAINT [FK_SetLogs_WorkoutLogs] FOREIGN KEY ([WorkoutLogId]) 
        REFERENCES [dbo].[WorkoutLogs]([WorkoutLogId]) ON DELETE CASCADE,
    CONSTRAINT [FK_SetLogs_Sets] FOREIGN KEY ([OriginalSetId]) 
        REFERENCES [dbo].[Sets]([SetId]) ON DELETE NO ACTION,
    CONSTRAINT [FK_SetLogs_Exercises] FOREIGN KEY ([ExerciseId]) 
        REFERENCES [dbo].[Exercises]([ExerciseId]) ON DELETE NO ACTION
);

-- Create indexes
CREATE INDEX [IX_SetLogs_WorkoutLogId] ON [dbo].[SetLogs]([WorkoutLogId]);
CREATE INDEX [IX_SetLogs_OriginalSetId] ON [dbo].[SetLogs]([OriginalSetId]);
CREATE INDEX [IX_SetLogs_ExerciseId] ON [dbo].[SetLogs]([ExerciseId]);
CREATE INDEX [IX_SetLogs_WorkoutLogId_SetOrder] ON [dbo].[SetLogs]([WorkoutLogId], [SetOrder], [SetNumber]);

PRINT 'SetLogs table created';

