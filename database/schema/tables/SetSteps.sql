-- SetSteps Table
-- Individual rep/weight segments within a set (supports drop sets, pyramids, etc.)

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

-- Create indexes
CREATE INDEX [IX_SetSteps_SetId] ON [dbo].[SetSteps]([SetId]);
CREATE UNIQUE INDEX [IX_SetSteps_SetId_StepOrder] ON [dbo].[SetSteps]([SetId], [StepOrder]);
