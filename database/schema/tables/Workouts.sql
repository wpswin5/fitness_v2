-- Workouts Table
-- Stores workout/exercise logs for users

CREATE TABLE [dbo].[Workouts] (
    [WorkoutId] INT PRIMARY KEY IDENTITY(1,1),
    [UserId] INT NOT NULL,
    [ExerciseName] NVARCHAR(255) NOT NULL,
    [DurationMinutes] INT NOT NULL,
    [CaloriesBurned] INT NOT NULL,
    [WorkoutDate] DATETIME2 NOT NULL,
    [Notes] NVARCHAR(MAX),
    [CreatedAt] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    [UpdatedAt] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    CONSTRAINT [FK_Workouts_Users] FOREIGN KEY ([UserId]) REFERENCES [dbo].[Users]([UserId]) ON DELETE CASCADE
);

-- Create indexes for common queries
CREATE INDEX [IX_Workouts_UserId] ON [dbo].[Workouts]([UserId]);
CREATE INDEX [IX_Workouts_WorkoutDate] ON [dbo].[Workouts]([WorkoutDate]);
