-- Seed test data for new program assignment tables
-- Version: 021
-- Created: 2026-03-03
-- Description: Add test program, program workouts, user program assignment,
--              and program workout logs for testing progress tracking.

-- Get existing test user
DECLARE @TestUserId UNIQUEIDENTIFIER;
DECLARE @TestAuth0Sub NVARCHAR(255) = 'auth0|test-user-seed';

SELECT @TestUserId = UserId FROM [dbo].[Users] WHERE Auth0Sub = @TestAuth0Sub;

IF @TestUserId IS NULL
BEGIN
    PRINT 'Test user not found. Run migration 015 first.';
    RETURN;
END

-- Get existing test workout
DECLARE @TestWorkoutId UNIQUEIDENTIFIER;
SELECT @TestWorkoutId = WorkoutId FROM [dbo].[Workouts] 
    WHERE Name = 'Test Full Body Workout' AND CreatorId = @TestUserId;

-- Step 1: Create a test program
DECLARE @TestProgramId UNIQUEIDENTIFIER;

IF NOT EXISTS (SELECT 1 FROM [dbo].[Programs] WHERE Name = 'Test Beginner Program' AND CreatorId = @TestUserId)
BEGIN
    SET @TestProgramId = NEWID();
    INSERT INTO [dbo].[Programs] (ProgramId, CreatorId, Name, Description, IsShared, DurationWeeks, CreatedAt, UpdatedAt)
    VALUES (
        @TestProgramId,
        @TestUserId,
        'Test Beginner Program',
        'A 2-week test program for validating program assignment and progress tracking',
        1,
        2,
        GETUTCDATE(),
        GETUTCDATE()
    );
    PRINT 'Created test program: Test Beginner Program';
END
ELSE
BEGIN
    SELECT @TestProgramId = ProgramId FROM [dbo].[Programs] WHERE Name = 'Test Beginner Program' AND CreatorId = @TestUserId;
    PRINT 'Test program already exists';
END

-- Step 2: Schedule workouts (3 days per week for 2 weeks)
IF @TestWorkoutId IS NOT NULL AND NOT EXISTS (
    SELECT 1 FROM [dbo].[ProgramWorkouts] WHERE ProgramId = @TestProgramId AND WeekNumber = 1 AND DayOfWeek = 1
)
BEGIN
    -- Week 1: Mon, Wed, Fri
    INSERT INTO [dbo].[ProgramWorkouts] (ProgramId, WorkoutId, WeekNumber, DayOfWeek, IsRestDay, CreatedAt)
    VALUES 
        (@TestProgramId, @TestWorkoutId, 1, 1, 0, GETUTCDATE()),  -- Monday
        (@TestProgramId, NULL,           1, 2, 1, GETUTCDATE()),  -- Tuesday (rest)
        (@TestProgramId, @TestWorkoutId, 1, 3, 0, GETUTCDATE()),  -- Wednesday
        (@TestProgramId, NULL,           1, 4, 1, GETUTCDATE()),  -- Thursday (rest)
        (@TestProgramId, @TestWorkoutId, 1, 5, 0, GETUTCDATE()),  -- Friday
        -- Week 2: Mon, Wed, Fri
        (@TestProgramId, @TestWorkoutId, 2, 1, 0, GETUTCDATE()),  -- Monday
        (@TestProgramId, NULL,           2, 2, 1, GETUTCDATE()),  -- Tuesday (rest)
        (@TestProgramId, @TestWorkoutId, 2, 3, 0, GETUTCDATE()),  -- Wednesday
        (@TestProgramId, NULL,           2, 4, 1, GETUTCDATE()),  -- Thursday (rest)
        (@TestProgramId, @TestWorkoutId, 2, 5, 0, GETUTCDATE());  -- Friday
    PRINT 'Created program workout schedule (2 weeks, 3 workout days + 2 rest days each)';
END
ELSE
BEGIN
    PRINT 'Program workouts already exist or test workout not found';
END

-- Step 3: Create a test assignment (user enrolled in the program)
DECLARE @TestAssignmentId UNIQUEIDENTIFIER;
DECLARE @TestStartDate DATE = CAST(GETUTCDATE() AS DATE);

IF NOT EXISTS (
    SELECT 1 FROM [dbo].[UserProgramAssignments] 
    WHERE UserId = @TestUserId AND ProgramId = @TestProgramId AND StartDate = @TestStartDate
)
BEGIN
    SET @TestAssignmentId = NEWID();
    INSERT INTO [dbo].[UserProgramAssignments] 
        (AssignmentId, UserId, ProgramId, StartDate, Status, CurrentWeek, CurrentDayOfWeek, CreatedAt, UpdatedAt)
    VALUES (
        @TestAssignmentId,
        @TestUserId,
        @TestProgramId,
        @TestStartDate,
        'active',
        1,
        1,
        GETUTCDATE(),
        GETUTCDATE()
    );
    PRINT 'Created test program assignment';
END
ELSE
BEGIN
    SELECT @TestAssignmentId = AssignmentId FROM [dbo].[UserProgramAssignments]
        WHERE UserId = @TestUserId AND ProgramId = @TestProgramId AND StartDate = @TestStartDate;
    PRINT 'Test program assignment already exists';
END

-- Step 4: Pre-populate ProgramWorkoutLogs for the assignment (non-rest days only)
IF @TestAssignmentId IS NOT NULL AND NOT EXISTS (
    SELECT 1 FROM [dbo].[ProgramWorkoutLogs] WHERE AssignmentId = @TestAssignmentId
)
BEGIN
    INSERT INTO [dbo].[ProgramWorkoutLogs]
        (ProgramWorkoutLogId, AssignmentId, WeekNumber, DayOfWeek, Status, ScheduledDate, CreatedAt, UpdatedAt)
    SELECT 
        NEWID(),
        @TestAssignmentId,
        pw.WeekNumber,
        pw.DayOfWeek,
        'pending',
        DATEADD(DAY, ((pw.WeekNumber - 1) * 7) + pw.DayOfWeek - 1, @TestStartDate),
        GETUTCDATE(),
        GETUTCDATE()
    FROM [dbo].[ProgramWorkouts] pw
    WHERE pw.ProgramId = @TestProgramId AND pw.IsRestDay = 0;

    PRINT 'Pre-populated ProgramWorkoutLogs for test assignment';
END
ELSE
BEGIN
    PRINT 'ProgramWorkoutLogs already exist for test assignment';
END

-- Summary
PRINT '';
PRINT '=== Additional Seed Data Summary ===';
PRINT 'Test Program ID: ' + CAST(@TestProgramId AS NVARCHAR(50));
PRINT 'Test Assignment ID: ' + CAST(ISNULL(@TestAssignmentId, 'N/A') AS NVARCHAR(50));
PRINT 'Program Schedule: 2 weeks, 3 workout days + 2 rest days per week';
PRINT 'ProgramWorkoutLogs: 6 entries (pending)';
PRINT '';
