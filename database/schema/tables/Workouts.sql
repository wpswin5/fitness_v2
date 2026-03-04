-- Workouts Table
-- Workout templates created by users

CREATE TABLE [dbo].[Workouts] (
    [WorkoutId] UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    [CreatorId] UNIQUEIDENTIFIER NOT NULL,
    [Name] NVARCHAR(255) NOT NULL,
    [Description] NVARCHAR(MAX),
    [IsShared] BIT NOT NULL DEFAULT 0,
    [DeletedAt] DATETIME2 NULL, -- Soft delete: NULL = active, non-null = deleted
    [CreatedAt] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    [UpdatedAt] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    CONSTRAINT [FK_Workouts_Users] FOREIGN KEY ([CreatorId]) 
        REFERENCES [dbo].[Users]([UserId]) ON DELETE CASCADE
);

-- Create indexes
CREATE INDEX [IX_Workouts_CreatorId] ON [dbo].[Workouts]([CreatorId]);
CREATE INDEX [IX_Workouts_IsShared] ON [dbo].[Workouts]([IsShared]);
CREATE INDEX [IX_Workouts_DeletedAt] ON [dbo].[Workouts]([DeletedAt]);
CREATE INDEX [IX_Workouts_Active_CreatorId] ON [dbo].[Workouts]([CreatorId]) WHERE [DeletedAt] IS NULL;
CREATE INDEX [IX_Workouts_Active_Shared] ON [dbo].[Workouts]([IsShared]) WHERE [DeletedAt] IS NULL AND [IsShared] = 1;
