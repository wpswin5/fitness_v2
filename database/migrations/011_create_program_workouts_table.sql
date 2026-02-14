-- Create ProgramWorkouts table
-- Version: 011
-- Created: 2026-02-13
-- Description: Many-to-many mapping of workouts to programs with scheduling

IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'ProgramWorkouts')
BEGIN
    CREATE TABLE [dbo].[ProgramWorkouts] (
        [ProgramId] UNIQUEIDENTIFIER NOT NULL,
        [WorkoutId] UNIQUEIDENTIFIER NULL,
        [WeekNumber] INT NOT NULL,
        [DayOfWeek] INT NOT NULL,
        [IsRestDay] BIT NOT NULL DEFAULT 0,
        [CreatedAt] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        CONSTRAINT [PK_ProgramWorkouts] PRIMARY KEY ([ProgramId], [WeekNumber], [DayOfWeek]),
        CONSTRAINT [FK_ProgramWorkouts_Programs] FOREIGN KEY ([ProgramId]) 
            REFERENCES [dbo].[Programs]([ProgramId]) ON DELETE CASCADE,
        CONSTRAINT [FK_ProgramWorkouts_Workouts] FOREIGN KEY ([WorkoutId]) 
            REFERENCES [dbo].[Workouts]([WorkoutId]) ON DELETE NO ACTION,
        CONSTRAINT [CK_ProgramWorkouts_DayOfWeek] CHECK ([DayOfWeek] >= 0 AND [DayOfWeek] <= 6),
        CONSTRAINT [CK_ProgramWorkouts_RestDay] CHECK (
            ([IsRestDay] = 1 AND [WorkoutId] IS NULL) OR 
            ([IsRestDay] = 0 AND [WorkoutId] IS NOT NULL)
        )
    );
    PRINT 'ProgramWorkouts table created';
END
ELSE
BEGIN
    PRINT 'ProgramWorkouts table already exists';
END

-- Create indexes (idempotent)
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_ProgramWorkouts_WorkoutId' AND object_id = OBJECT_ID('dbo.ProgramWorkouts'))
    CREATE INDEX [IX_ProgramWorkouts_WorkoutId] ON [dbo].[ProgramWorkouts]([WorkoutId]);

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_ProgramWorkouts_ProgramId_WeekNumber' AND object_id = OBJECT_ID('dbo.ProgramWorkouts'))
    CREATE INDEX [IX_ProgramWorkouts_ProgramId_WeekNumber] ON [dbo].[ProgramWorkouts]([ProgramId], [WeekNumber]);

