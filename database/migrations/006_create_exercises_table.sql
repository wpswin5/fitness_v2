-- Create Exercises table
-- Version: 006
-- Created: 2026-02-13
-- Description: Master list of exercises available in the system

CREATE TABLE [dbo].[Exercises] (
    [ExerciseId] UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    [Name] NVARCHAR(255) NOT NULL,
    [Description] NVARCHAR(MAX),
    [EquipmentRequired] NVARCHAR(MAX), -- JSON array of equipment needed
    [PrimaryMuscleGroup] NVARCHAR(100), -- e.g., "chest", "back", "legs"
    [DifficultyLevel] NVARCHAR(50), -- "beginner", "intermediate", "advanced"
    [Instructions] NVARCHAR(MAX),
    [CreatedAt] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    [UpdatedAt] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    CONSTRAINT [UQ_Exercises_Name] UNIQUE ([Name])
);

-- Create indexes for common queries
CREATE INDEX [IX_Exercises_PrimaryMuscleGroup] ON [dbo].[Exercises]([PrimaryMuscleGroup]);
CREATE INDEX [IX_Exercises_DifficultyLevel] ON [dbo].[Exercises]([DifficultyLevel]);

PRINT 'Exercises table created';

