-- Add soft delete support to content tables
-- Version: 017
-- Created: 2026-03-03
-- Description: Add DeletedAt column to Exercises, Workouts, and Programs.
--              NULL = active record, non-null = soft-deleted.
--              Logs are never soft-deleted (historical records).
--              Sets/SetSteps cascade with their parent Workout.
--              ProgramWorkouts cascade with their parent Program.

-- ============================================================================
-- Exercises
-- ============================================================================
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('dbo.Exercises') AND name = 'DeletedAt')
BEGIN
    ALTER TABLE [dbo].[Exercises]
        ADD [DeletedAt] DATETIME2 NULL;
    PRINT 'Added DeletedAt column to Exercises table';
END
ELSE
BEGIN
    PRINT 'DeletedAt column already exists on Exercises table';
END

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_Exercises_DeletedAt' AND object_id = OBJECT_ID('dbo.Exercises'))
BEGIN
    CREATE INDEX [IX_Exercises_DeletedAt] ON [dbo].[Exercises]([DeletedAt]);
    PRINT 'Index IX_Exercises_DeletedAt created';
END

-- ============================================================================
-- Workouts
-- ============================================================================
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('dbo.Workouts') AND name = 'DeletedAt')
BEGIN
    ALTER TABLE [dbo].[Workouts]
        ADD [DeletedAt] DATETIME2 NULL;
    PRINT 'Added DeletedAt column to Workouts table';
END
ELSE
BEGIN
    PRINT 'DeletedAt column already exists on Workouts table';
END

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_Workouts_DeletedAt' AND object_id = OBJECT_ID('dbo.Workouts'))
BEGIN
    CREATE INDEX [IX_Workouts_DeletedAt] ON [dbo].[Workouts]([DeletedAt]);
    PRINT 'Index IX_Workouts_DeletedAt created';
END

-- ============================================================================
-- Programs
-- ============================================================================
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('dbo.Programs') AND name = 'DeletedAt')
BEGIN
    ALTER TABLE [dbo].[Programs]
        ADD [DeletedAt] DATETIME2 NULL;
    PRINT 'Added DeletedAt column to Programs table';
END
ELSE
BEGIN
    PRINT 'DeletedAt column already exists on Programs table';
END

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_Programs_DeletedAt' AND object_id = OBJECT_ID('dbo.Programs'))
BEGIN
    CREATE INDEX [IX_Programs_DeletedAt] ON [dbo].[Programs]([DeletedAt]);
    PRINT 'Index IX_Programs_DeletedAt created';
END
