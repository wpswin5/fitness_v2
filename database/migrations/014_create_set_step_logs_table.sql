-- Create SetStepLogs table
-- Version: 014
-- Created: 2026-02-13
-- Description: Individual step execution within a completed set (actual reps/weight per step)

CREATE TABLE [dbo].[SetStepLogs] (
    [SetStepLogId] UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    [SetLogId] UNIQUEIDENTIFIER NOT NULL,
    [OriginalSetStepId] UNIQUEIDENTIFIER NULL, -- Null for ad-hoc steps
    [StepOrder] INT NOT NULL, -- Order within the set
    [CompletedReps] INT NOT NULL,
    [CompletedWeight] DECIMAL(10, 2), -- Null for bodyweight exercises
    [CompletedTimeSeconds] INT, -- Time to complete this step (optional)
    [RestTimeAfterSeconds] INT, -- Rest taken after this step (optional)
    [Notes] NVARCHAR(MAX),
    [CreatedAt] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    CONSTRAINT [FK_SetStepLogs_SetLogs] FOREIGN KEY ([SetLogId]) 
        REFERENCES [dbo].[SetLogs]([SetLogId]) ON DELETE CASCADE,
    CONSTRAINT [FK_SetStepLogs_SetSteps] FOREIGN KEY ([OriginalSetStepId]) 
        REFERENCES [dbo].[SetSteps]([SetStepId]) ON DELETE NO ACTION
);

-- Create indexes
CREATE INDEX [IX_SetStepLogs_SetLogId] ON [dbo].[SetStepLogs]([SetLogId]);
CREATE INDEX [IX_SetStepLogs_OriginalSetStepId] ON [dbo].[SetStepLogs]([OriginalSetStepId]);
CREATE UNIQUE INDEX [IX_SetStepLogs_SetLogId_StepOrder] ON [dbo].[SetStepLogs]([SetLogId], [StepOrder]);

PRINT 'SetStepLogs table created';

