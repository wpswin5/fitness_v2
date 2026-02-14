-- Create SetSteps table
-- Version: 009
-- Created: 2026-02-13
-- Description: Individual rep/weight segments within a set (supports drop sets, pyramids, etc.)

IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'SetSteps')
BEGIN
    CREATE TABLE [dbo].[SetSteps] (
        [SetStepId] UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        [SetId] UNIQUEIDENTIFIER NOT NULL,
        [StepOrder] INT NOT NULL,
        [PlannedReps] INT NOT NULL,
        [PlannedWeight] DECIMAL(10, 2),
        [CreatedAt] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        [UpdatedAt] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        CONSTRAINT [FK_SetSteps_Sets] FOREIGN KEY ([SetId]) 
            REFERENCES [dbo].[Sets]([SetId]) ON DELETE CASCADE
    );
    PRINT 'SetSteps table created';
END
ELSE
BEGIN
    PRINT 'SetSteps table already exists';
END

-- Create indexes (idempotent)
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_SetSteps_SetId' AND object_id = OBJECT_ID('dbo.SetSteps'))
    CREATE INDEX [IX_SetSteps_SetId] ON [dbo].[SetSteps]([SetId]);

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_SetSteps_SetId_StepOrder' AND object_id = OBJECT_ID('dbo.SetSteps'))
    CREATE UNIQUE INDEX [IX_SetSteps_SetId_StepOrder] ON [dbo].[SetSteps]([SetId], [StepOrder]);

