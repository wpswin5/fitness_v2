-- Add performance indexes for common query patterns
-- Version: 020
-- Created: 2026-03-03
-- Description: Composite and filtered indexes to optimize frequent API queries.
--              Covers: active record filtering, user content lookups, exercise search,
--              log history queries, and program progress lookups.

-- Required for filtered indexes on SQL Server
SET QUOTED_IDENTIFIER ON;
SET ANSI_NULLS ON;

-- ============================================================================
-- Filtered indexes for active (non-deleted) records
-- These are the most common queries - almost all reads exclude deleted items
-- ============================================================================

-- Active exercises (visible to everyone, filtered by muscle group/difficulty)
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_Exercises_Active_MuscleGroup' AND object_id = OBJECT_ID('dbo.Exercises'))
    CREATE INDEX [IX_Exercises_Active_MuscleGroup]
        ON [dbo].[Exercises]([PrimaryMuscleGroup])
        WHERE [DeletedAt] IS NULL;

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_Exercises_Active_CreatorId' AND object_id = OBJECT_ID('dbo.Exercises'))
    CREATE INDEX [IX_Exercises_Active_CreatorId]
        ON [dbo].[Exercises]([CreatorId])
        WHERE [DeletedAt] IS NULL;

-- Active workouts by creator (user's own workouts)
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_Workouts_Active_CreatorId' AND object_id = OBJECT_ID('dbo.Workouts'))
    CREATE INDEX [IX_Workouts_Active_CreatorId]
        ON [dbo].[Workouts]([CreatorId])
        WHERE [DeletedAt] IS NULL;

-- Active shared workouts (browseable by all users)
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_Workouts_Active_Shared' AND object_id = OBJECT_ID('dbo.Workouts'))
    CREATE INDEX [IX_Workouts_Active_Shared]
        ON [dbo].[Workouts]([IsShared])
        WHERE [DeletedAt] IS NULL AND [IsShared] = 1;

-- Active programs by creator
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_Programs_Active_CreatorId' AND object_id = OBJECT_ID('dbo.Programs'))
    CREATE INDEX [IX_Programs_Active_CreatorId]
        ON [dbo].[Programs]([CreatorId])
        WHERE [DeletedAt] IS NULL;

-- Active shared programs
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_Programs_Active_Shared' AND object_id = OBJECT_ID('dbo.Programs'))
    CREATE INDEX [IX_Programs_Active_Shared]
        ON [dbo].[Programs]([IsShared])
        WHERE [DeletedAt] IS NULL AND [IsShared] = 1;

-- ============================================================================
-- Exercise performance query indexes
-- Common query: "show me my history for exercise X"
-- ============================================================================

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_SetLogs_ExerciseId_WorkoutLogId' AND object_id = OBJECT_ID('dbo.SetLogs'))
    CREATE INDEX [IX_SetLogs_ExerciseId_WorkoutLogId]
        ON [dbo].[SetLogs]([ExerciseId], [WorkoutLogId]);

-- ============================================================================
-- Workout log date range queries
-- Common query: "show me workouts between date X and Y"
-- ============================================================================

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_WorkoutLogs_UserId_ProgramId' AND object_id = OBJECT_ID('dbo.WorkoutLogs'))
    CREATE INDEX [IX_WorkoutLogs_UserId_ProgramId]
        ON [dbo].[WorkoutLogs]([UserId], [ProgramId])
        WHERE [ProgramId] IS NOT NULL;

PRINT 'Performance indexes created successfully';
