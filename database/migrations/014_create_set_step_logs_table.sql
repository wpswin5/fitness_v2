-- Create SetStepLogs table
-- Version: 014
-- Created: 2026-02-13
-- Description: Individual step execution within a completed set (actual reps/weight per step)

IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'SetStepLogs')
BEGIN
    CREATE TABLE [dbo].[SetStepLogs] (
        [SetStepLogId] UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        [SetLogId] UNIQUEIDENTIFIER NOT NULL,
        [OriginalSetStepId] UNIQUEIDENTIFIER NULL,
        [StepOrder] INT NOT NULL,
        [CompletedReps] INT NOT NULL,
        [CompletedWeight] DECIMAL(10, 2),
        [CompletedTimeSeconds] INT,
        [RestTimeAfterSeconds] INT,
        [Notes] NVARCHAR(MAX),
        [CreatedAt] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        CONSTRAINT [FK_SetStepLogs_SetLogs] FOREIGN KEY ([SetLogId]) 
            REFERENCES [dbo].[SetLogs]([SetLogId]) ON DELETE CASCADE,
        CONSTRAINT [FK_SetStepLogs_SetSteps] FOREIGN KEY ([OriginalSetStepId]) 
            REFERENCES [dbo].[SetSteps]([SetStepId]) ON DELETE NO ACTION
    );
    PRINT 'SetStepLogs table created';
END
ELSE
BEGIN
    PRINT 'SetStepLogs table already exists';
END

-- Create indexes (idempotent)
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_SetStepLogs_SetLogId' AND object_id = OBJECT_ID('dbo.SetStepLogs'))
    CREATE INDEX [IX_SetStepLogs_SetLogId] ON [dbo].[SetStepLogs]([SetLogId]);

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_SetStepLogs_OriginalSetStepId' AND object_id = OBJECT_ID('dbo.SetStepLogs'))
    CREATE INDEX [IX_SetStepLogs_OriginalSetStepId] ON [dbo].[SetStepLogs]([OriginalSetStepId]);

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_SetStepLogs_SetLogId_StepOrder' AND object_id = OBJECT_ID('dbo.SetStepLogs'))
    CREATE UNIQUE INDEX [IX_SetStepLogs_SetLogId_StepOrder] ON [dbo].[SetStepLogs]([SetLogId], [StepOrder]);

