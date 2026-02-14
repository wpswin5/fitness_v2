-- Sets Table
-- Individual exercise entries within a workout

CREATE TABLE [dbo].[Sets] (
    [SetId] UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    [WorkoutId] UNIQUEIDENTIFIER NOT NULL,
    [SetOrder] INT NOT NULL,
    [ExerciseId] UNIQUEIDENTIFIER NOT NULL,
    [NumSets] INT NOT NULL DEFAULT 1,
    [RestSeconds] INT,
    [Notes] NVARCHAR(MAX),
    [CreatedAt] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    [UpdatedAt] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    CONSTRAINT [FK_Sets_Workouts] FOREIGN KEY ([WorkoutId]) 
        REFERENCES [dbo].[Workouts]([WorkoutId]) ON DELETE CASCADE,
    CONSTRAINT [FK_Sets_Exercises] FOREIGN KEY ([ExerciseId]) 
        REFERENCES [dbo].[Exercises]([ExerciseId]) ON DELETE NO ACTION
);

-- Create indexes
CREATE INDEX [IX_Sets_WorkoutId] ON [dbo].[Sets]([WorkoutId]);
CREATE INDEX [IX_Sets_ExerciseId] ON [dbo].[Sets]([ExerciseId]);
CREATE UNIQUE INDEX [IX_Sets_WorkoutId_SetOrder] ON [dbo].[Sets]([WorkoutId], [SetOrder]);
