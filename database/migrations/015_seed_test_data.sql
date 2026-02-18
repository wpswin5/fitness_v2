-- Seed Test Data
-- Version: 015
-- Description: Add test user, exercises, workout, and related data for testing

-- Declare variables for test user
DECLARE @TestUserId UNIQUEIDENTIFIER = NEWID();
DECLARE @TestAuth0Sub NVARCHAR(255) = 'auth0|test-user-seed';
DECLARE @TestEmail NVARCHAR(255) = 'test@fitness-app.example.com';

-- Step 1: Insert test user if it doesn't exist
IF NOT EXISTS (SELECT 1 FROM [dbo].[Users] WHERE Auth0Sub = @TestAuth0Sub)
BEGIN
    INSERT INTO [dbo].[Users] (UserId, Auth0Sub, Email, FirstName, LastName, CreatedAt, UpdatedAt)
    VALUES (@TestUserId, @TestAuth0Sub, @TestEmail, 'Test', 'User', GETUTCDATE(), GETUTCDATE());
    
    PRINT 'Created test user: ' + @TestAuth0Sub;
END
ELSE
BEGIN
    SELECT @TestUserId = UserId FROM [dbo].[Users] WHERE Auth0Sub = @TestAuth0Sub;
    PRINT 'Test user already exists: ' + @TestAuth0Sub;
END

-- Step 2: Insert test exercises if they don't exist
DECLARE @PushupExerciseId UNIQUEIDENTIFIER;
DECLARE @SquatExerciseId UNIQUEIDENTIFIER;
DECLARE @BenchPressExerciseId UNIQUEIDENTIFIER;

-- Pushup
IF NOT EXISTS (SELECT 1 FROM [dbo].[Exercises] WHERE Name = 'Pushup')
BEGIN
    SET @PushupExerciseId = NEWID();
    INSERT INTO [dbo].[Exercises] 
        (ExerciseId, Name, Description, PrimaryMuscleGroup, DifficultyLevel, Instructions, CreatedAt, UpdatedAt)
    VALUES (
        @PushupExerciseId,
        'Pushup',
        'Classic bodyweight pushing exercise',
        'Chest',
        'Beginner',
        'Start in plank position. Lower body until chest nearly touches ground, then push back up.',
        GETUTCDATE(),
        GETUTCDATE()
    );
    PRINT 'Created exercise: Pushup';
END
ELSE
BEGIN
    SELECT @PushupExerciseId = ExerciseId FROM [dbo].[Exercises] WHERE Name = 'Pushup';
END

-- Squat
IF NOT EXISTS (SELECT 1 FROM [dbo].[Exercises] WHERE Name = 'Squat')
BEGIN
    SET @SquatExerciseId = NEWID();
    INSERT INTO [dbo].[Exercises] 
        (ExerciseId, Name, Description, PrimaryMuscleGroup, DifficultyLevel, Instructions, CreatedAt, UpdatedAt)
    VALUES (
        @SquatExerciseId,
        'Squat',
        'Compound lower body exercise',
        'Legs',
        'Intermediate',
        'Stand with feet shoulder width apart. Lower hips back and down, keeping chest upright, then drive back up.',
        GETUTCDATE(),
        GETUTCDATE()
    );
    PRINT 'Created exercise: Squat';
END
ELSE
BEGIN
    SELECT @SquatExerciseId = ExerciseId FROM [dbo].[Exercises] WHERE Name = 'Squat';
END

-- Bench Press
IF NOT EXISTS (SELECT 1 FROM [dbo].[Exercises] WHERE Name = 'Bench Press')
BEGIN
    SET @BenchPressExerciseId = NEWID();
    INSERT INTO [dbo].[Exercises] 
        (ExerciseId, Name, Description, PrimaryMuscleGroup, DifficultyLevel, Instructions, CreatedAt, UpdatedAt)
    VALUES (
        @BenchPressExerciseId,
        'Bench Press',
        'Classic upper body pressing exercise',
        'Chest',
        'Intermediate',
        'Lie on bench. Press barbell from chest level to full arm extension, then control back down.',
        GETUTCDATE(),
        GETUTCDATE()
    );
    PRINT 'Created exercise: Bench Press';
END
ELSE
BEGIN
    SELECT @BenchPressExerciseId = ExerciseId FROM [dbo].[Exercises] WHERE Name = 'Bench Press';
END

-- Step 3: Create test workout if it doesn't exist
DECLARE @TestWorkoutId UNIQUEIDENTIFIER;

IF NOT EXISTS (SELECT 1 FROM [dbo].[Workouts] WHERE Name = 'Test Full Body Workout' AND CreatorId = @TestUserId)
BEGIN
    SET @TestWorkoutId = NEWID();
    INSERT INTO [dbo].[Workouts] (WorkoutId, CreatorId, Name, Description, IsShared, CreatedAt, UpdatedAt)
    VALUES (
        @TestWorkoutId,
        @TestUserId,
        'Test Full Body Workout',
        'A full body test workout with pushups, squats, and bench press',
        0,
        GETUTCDATE(),
        GETUTCDATE()
    );
    PRINT 'Created workout: Test Full Body Workout';
END
ELSE
BEGIN
    SELECT @TestWorkoutId = WorkoutId FROM [dbo].[Workouts] WHERE Name = 'Test Full Body Workout' AND CreatorId = @TestUserId;
    PRINT 'Test workout already exists';
END

-- Step 4: Create test sets and set steps
DECLARE @Set1Id UNIQUEIDENTIFIER;
DECLARE @Set2Id UNIQUEIDENTIFIER;
DECLARE @Set3Id UNIQUEIDENTIFIER;

-- Set 1: Pushups
IF NOT EXISTS (SELECT 1 FROM [dbo].[Sets] WHERE WorkoutId = @TestWorkoutId AND SetOrder = 1)
BEGIN
    SET @Set1Id = NEWID();
    INSERT INTO [dbo].[Sets] (SetId, WorkoutId, SetOrder, ExerciseId, NumSets, RestSeconds, CreatedAt, UpdatedAt)
    VALUES (@Set1Id, @TestWorkoutId, 1, @PushupExerciseId, 3, 90, GETUTCDATE(), GETUTCDATE());
    
    -- Add set steps for pushups
    INSERT INTO [dbo].[SetSteps] (SetStepId, SetId, StepOrder, PlannedReps, PlannedWeight, CreatedAt, UpdatedAt)
    VALUES 
        (NEWID(), @Set1Id, 1, 10, NULL, GETUTCDATE(), GETUTCDATE()),
        (NEWID(), @Set1Id, 2, 15, NULL, GETUTCDATE(), GETUTCDATE()),
        (NEWID(), @Set1Id, 3, 20, NULL, GETUTCDATE(), GETUTCDATE());
    
    PRINT 'Created Set 1: Pushups with steps';
END

-- Set 2: Squats
IF NOT EXISTS (SELECT 1 FROM [dbo].[Sets] WHERE WorkoutId = @TestWorkoutId AND SetOrder = 2)
BEGIN
    SET @Set2Id = NEWID();
    INSERT INTO [dbo].[Sets] (SetId, WorkoutId, SetOrder, ExerciseId, NumSets, RestSeconds, CreatedAt, UpdatedAt)
    VALUES (@Set2Id, @TestWorkoutId, 2, @SquatExerciseId, 3, 120, GETUTCDATE(), GETUTCDATE());
    
    -- Add set steps for squats
    INSERT INTO [dbo].[SetSteps] (SetStepId, SetId, StepOrder, PlannedReps, PlannedWeight, CreatedAt, UpdatedAt)
    VALUES 
        (NEWID(), @Set2Id, 1, 12, 185.00, GETUTCDATE(), GETUTCDATE()),
        (NEWID(), @Set2Id, 2, 10, 205.00, GETUTCDATE(), GETUTCDATE()),
        (NEWID(), @Set2Id, 3, 8, 225.00, GETUTCDATE(), GETUTCDATE());
    
    PRINT 'Created Set 2: Squats with steps';
END

-- Set 3: Bench Press
IF NOT EXISTS (SELECT 1 FROM [dbo].[Sets] WHERE WorkoutId = @TestWorkoutId AND SetOrder = 3)
BEGIN
    SET @Set3Id = NEWID();
    INSERT INTO [dbo].[Sets] (SetId, WorkoutId, SetOrder, ExerciseId, NumSets, RestSeconds, CreatedAt, UpdatedAt)
    VALUES (@Set3Id, @TestWorkoutId, 3, @BenchPressExerciseId, 4, 120, GETUTCDATE(), GETUTCDATE());
    
    -- Add set steps for bench press
    INSERT INTO [dbo].[SetSteps] (SetStepId, SetId, StepOrder, PlannedReps, PlannedWeight, CreatedAt, UpdatedAt)
    VALUES 
        (NEWID(), @Set3Id, 1, 8, 185.00, GETUTCDATE(), GETUTCDATE()),
        (NEWID(), @Set3Id, 2, 6, 205.00, GETUTCDATE(), GETUTCDATE()),
        (NEWID(), @Set3Id, 3, 4, 225.00, GETUTCDATE(), GETUTCDATE()),
        (NEWID(), @Set3Id, 4, 8, 185.00, GETUTCDATE(), GETUTCDATE());
    
    PRINT 'Created Set 3: Bench Press with steps';
END

-- Step 5: Create a test workout log
DECLARE @TestWorkoutLogId UNIQUEIDENTIFIER;
DECLARE @TestStartTime DATETIME2 = GETUTCDATE();
DECLARE @TestEndTime DATETIME2 = DATEADD(MINUTE, 60, @TestStartTime);

IF NOT EXISTS (SELECT 1 FROM [dbo].[WorkoutLogs] WHERE UserId = @TestUserId AND CAST(StartTime AS DATE) = CAST(GETUTCDATE() AS DATE))
BEGIN
    SET @TestWorkoutLogId = NEWID();
    INSERT INTO [dbo].[WorkoutLogs] (WorkoutLogId, UserId, OriginalWorkoutId, StartTime, EndTime, Notes, CreatedAt)
    VALUES (
        @TestWorkoutLogId,
        @TestUserId,
        @TestWorkoutId,
        @TestStartTime,
        @TestEndTime,
        'Test workout log created for validation',
        GETUTCDATE()
    );
    PRINT 'Created test workout log';
END
ELSE
BEGIN
    PRINT 'Workout log already exists for today';
END

-- Summary
PRINT '';
PRINT '=== Seed Data Summary ===';
PRINT 'Test User ID: ' + CAST(@TestUserId AS NVARCHAR(50));
PRINT 'Test User Auth0Sub: ' + @TestAuth0Sub;
PRINT 'Test Workout ID: ' + CAST(@TestWorkoutId AS NVARCHAR(50));
PRINT 'Exercises Count: 3 (Pushup, Squat, Bench Press)';
PRINT 'Sets: 3 with total 10 SetSteps';
PRINT 'Workout Log ID: ' + CAST(@TestWorkoutLogId AS NVARCHAR(50));
PRINT '';
PRINT 'Ready for testing!';
