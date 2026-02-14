-- Create Workouts table
-- Version: 007
-- Created: 2026-02-13
-- Description: Workout templates created by users

CREATE TABLE [dbo].[Workouts] (
    [WorkoutId] UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    [CreatorId] UNIQUEIDENTIFIER NOT NULL,
    [Name] NVARCHAR(255) NOT NULL,
    [Description] NVARCHAR(MAX),
    [IsShared] BIT NOT NULL DEFAULT 0, -- Whether other users can see/use this workout
    [CreatedAt] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    [UpdatedAt] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    CONSTRAINT [FK_Workouts_Users] FOREIGN KEY ([CreatorId]) 
        REFERENCES [dbo].[Users]([UserId]) ON DELETE CASCADE
);

-- Create indexes
CREATE INDEX [IX_Workouts_CreatorId] ON [dbo].[Workouts]([CreatorId]);
CREATE INDEX [IX_Workouts_IsShared] ON [dbo].[Workouts]([IsShared]) WHERE [IsShared] = 1;

PRINT 'Workouts table created';

