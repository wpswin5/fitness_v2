-- Exercises Table
-- Master list of exercises available in the system

CREATE TABLE [dbo].[Exercises] (
    [ExerciseId] UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    [Name] NVARCHAR(255) NOT NULL,
    [Description] NVARCHAR(MAX),
    [EquipmentRequired] NVARCHAR(MAX), -- JSON array of equipment needed
    [PrimaryMuscleGroup] NVARCHAR(100),
    [DifficultyLevel] NVARCHAR(50),
    [Instructions] NVARCHAR(MAX),
    [CreatedAt] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    [UpdatedAt] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    CONSTRAINT [UQ_Exercises_Name] UNIQUE ([Name])
);

-- Create indexes
CREATE INDEX [IX_Exercises_PrimaryMuscleGroup] ON [dbo].[Exercises]([PrimaryMuscleGroup]);
CREATE INDEX [IX_Exercises_DifficultyLevel] ON [dbo].[Exercises]([DifficultyLevel]);
