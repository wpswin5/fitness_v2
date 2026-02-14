-- Drop legacy and test tables
-- Version: 004
-- Created: 2026-02-13
-- Description: Clean up old schema before implementing new fitness app design

-- Drop the old Workouts table (incompatible with new design)
IF OBJECT_ID('dbo.Workouts', 'U') IS NOT NULL
BEGIN
    DROP TABLE [dbo].[Workouts];
    PRINT 'Dropped legacy Workouts table';
END

-- Drop test tables
IF OBJECT_ID('dbo.Test', 'U') IS NOT NULL
BEGIN
    DROP TABLE [dbo].[Test];
    PRINT 'Dropped Test table';
END

