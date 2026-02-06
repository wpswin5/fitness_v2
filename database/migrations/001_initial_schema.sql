-- Initial schema migration: Create base tables
-- Version: 001
-- Created: 2026-02-05

-- Create Users table
CREATE TABLE [dbo].[Users] (
    [UserId] INT PRIMARY KEY IDENTITY(1,1),
    [Username] NVARCHAR(100) NOT NULL UNIQUE,
    [Email] NVARCHAR(255) NOT NULL UNIQUE,
    [FirstName] NVARCHAR(100) NOT NULL,
    [LastName] NVARCHAR(100) NOT NULL,
    [CreatedAt] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    [UpdatedAt] DATETIME2 NOT NULL DEFAULT GETUTCDATE()
);

-- Create Workouts table
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

-- Create indexes
CREATE INDEX [IX_Workouts_UserId] ON [dbo].[Workouts]([UserId]);
CREATE INDEX [IX_Workouts_WorkoutDate] ON [dbo].[Workouts]([WorkoutDate]);
