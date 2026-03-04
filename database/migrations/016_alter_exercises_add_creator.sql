-- Alter Exercises table to add creator ownership
-- Version: 016
-- Created: 2026-03-03
-- Description: Add CreatorId FK to Exercises for ownership tracking.
--              NULL CreatorId = system/admin-seeded exercise.
--              Non-null = user-created, only modifiable/deletable by creator or admin.

-- Add CreatorId column if it doesn't exist
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('dbo.Exercises') AND name = 'CreatorId')
BEGIN
    ALTER TABLE [dbo].[Exercises]
        ADD [CreatorId] UNIQUEIDENTIFIER NULL;

    ALTER TABLE [dbo].[Exercises]
        ADD CONSTRAINT [FK_Exercises_Users] FOREIGN KEY ([CreatorId])
            REFERENCES [dbo].[Users]([UserId]) ON DELETE SET NULL;

    PRINT 'Added CreatorId column to Exercises table';
END
ELSE
BEGIN
    PRINT 'CreatorId column already exists on Exercises table';
END

-- Create index on CreatorId
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_Exercises_CreatorId' AND object_id = OBJECT_ID('dbo.Exercises'))
BEGIN
    CREATE INDEX [IX_Exercises_CreatorId] ON [dbo].[Exercises]([CreatorId]);
    PRINT 'Index IX_Exercises_CreatorId created';
END
