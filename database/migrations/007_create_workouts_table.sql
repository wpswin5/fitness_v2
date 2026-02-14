-- Create Workouts table
-- Version: 007
-- Created: 2026-02-13
-- Description: Workout templates created by users

IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'Workouts')
BEGIN
    CREATE TABLE [dbo].[Workouts] (
        [WorkoutId] UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        [CreatorId] UNIQUEIDENTIFIER NOT NULL,
        [Name] NVARCHAR(255) NOT NULL,
        [Description] NVARCHAR(MAX),
        [IsShared] BIT NOT NULL DEFAULT 0,
        [CreatedAt] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        [UpdatedAt] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        CONSTRAINT [FK_Workouts_Users] FOREIGN KEY ([CreatorId]) 
            REFERENCES [dbo].[Users]([UserId]) ON DELETE CASCADE
    );
    PRINT 'Workouts table created';
END
ELSE
BEGIN
    PRINT 'Workouts table already exists';
END

-- Create indexes (idempotent)
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_Workouts_CreatorId' AND object_id = OBJECT_ID('dbo.Workouts'))
BEGIN
    CREATE INDEX [IX_Workouts_CreatorId] ON [dbo].[Workouts]([CreatorId]);
    PRINT 'Index IX_Workouts_CreatorId created';
END

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_Workouts_IsShared' AND object_id = OBJECT_ID('dbo.Workouts'))
BEGIN
    CREATE INDEX [IX_Workouts_IsShared] ON [dbo].[Workouts]([IsShared]);
    PRINT 'Index IX_Workouts_IsShared created';
END

