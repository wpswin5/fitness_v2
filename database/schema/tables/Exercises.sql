-- Exercises Table
-- Master list of exercises available in the system

CREATE TABLE [dbo].[Exercises] (
    [ExerciseId] UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    [CreatorId] UNIQUEIDENTIFIER NULL, -- NULL = system/admin-seeded, non-null = user-created
    [Name] NVARCHAR(255) NOT NULL,
    [Description] NVARCHAR(MAX),
    [EquipmentRequired] NVARCHAR(MAX), -- JSON array of equipment needed
    [PrimaryMuscleGroup] NVARCHAR(100),
    [DifficultyLevel] NVARCHAR(50),
    [Instructions] NVARCHAR(MAX),
    [DeletedAt] DATETIME2 NULL, -- Soft delete: NULL = active, non-null = deleted
    [CreatedAt] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    [UpdatedAt] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    CONSTRAINT [UQ_Exercises_Name] UNIQUE ([Name]),
    CONSTRAINT [FK_Exercises_Users] FOREIGN KEY ([CreatorId])
        REFERENCES [dbo].[Users]([UserId]) ON DELETE SET NULL
);

-- Create indexes
CREATE INDEX [IX_Exercises_CreatorId] ON [dbo].[Exercises]([CreatorId]);
CREATE INDEX [IX_Exercises_PrimaryMuscleGroup] ON [dbo].[Exercises]([PrimaryMuscleGroup]);
CREATE INDEX [IX_Exercises_DifficultyLevel] ON [dbo].[Exercises]([DifficultyLevel]);
CREATE INDEX [IX_Exercises_DeletedAt] ON [dbo].[Exercises]([DeletedAt]);
CREATE INDEX [IX_Exercises_Active_MuscleGroup] ON [dbo].[Exercises]([PrimaryMuscleGroup]) WHERE [DeletedAt] IS NULL;
CREATE INDEX [IX_Exercises_Active_CreatorId] ON [dbo].[Exercises]([CreatorId]) WHERE [DeletedAt] IS NULL;
