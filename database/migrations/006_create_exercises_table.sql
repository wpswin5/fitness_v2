-- Create Exercises table
-- Version: 006
-- Created: 2026-02-13
-- Description: Master list of exercises available in the system

IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'Exercises')
BEGIN
    CREATE TABLE [dbo].[Exercises] (
        [ExerciseId] UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        [Name] NVARCHAR(255) NOT NULL,
        [Description] NVARCHAR(MAX),
        [EquipmentRequired] NVARCHAR(MAX),
        [PrimaryMuscleGroup] NVARCHAR(100),
        [DifficultyLevel] NVARCHAR(50),
        [Instructions] NVARCHAR(MAX),
        [CreatedAt] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        [UpdatedAt] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        CONSTRAINT [UQ_Exercises_Name] UNIQUE ([Name])
    );
    PRINT 'Exercises table created';
END
ELSE
BEGIN
    PRINT 'Exercises table already exists';
END

-- Create indexes (idempotent)
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_Exercises_PrimaryMuscleGroup' AND object_id = OBJECT_ID('dbo.Exercises'))
    CREATE INDEX [IX_Exercises_PrimaryMuscleGroup] ON [dbo].[Exercises]([PrimaryMuscleGroup]);

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_Exercises_DifficultyLevel' AND object_id = OBJECT_ID('dbo.Exercises'))
    CREATE INDEX [IX_Exercises_DifficultyLevel] ON [dbo].[Exercises]([DifficultyLevel]);

