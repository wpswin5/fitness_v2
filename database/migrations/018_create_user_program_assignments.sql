-- Create UserProgramAssignments table
-- Version: 018
-- Created: 2026-03-03
-- Description: Tracks user enrollment in programs. A user can start the same
--              program multiple times (different start_date). Status tracks
--              lifecycle: active → completed/paused/abandoned.

IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'UserProgramAssignments')
BEGIN
    CREATE TABLE [dbo].[UserProgramAssignments] (
        [AssignmentId] UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        [UserId] UNIQUEIDENTIFIER NOT NULL,
        [ProgramId] UNIQUEIDENTIFIER NOT NULL,
        [StartDate] DATE NOT NULL,
        [Status] NVARCHAR(20) NOT NULL DEFAULT 'active',
        [CurrentWeek] INT NOT NULL DEFAULT 1,
        [CurrentDayOfWeek] INT NOT NULL DEFAULT 0,
        [CompletedAt] DATETIME2 NULL,
        [CreatedAt] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        [UpdatedAt] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        CONSTRAINT [FK_UserProgramAssignments_Users] FOREIGN KEY ([UserId])
            REFERENCES [dbo].[Users]([UserId]) ON DELETE CASCADE,
        CONSTRAINT [FK_UserProgramAssignments_Programs] FOREIGN KEY ([ProgramId])
            REFERENCES [dbo].[Programs]([ProgramId]) ON DELETE NO ACTION,
        CONSTRAINT [CK_UserProgramAssignments_Status] CHECK (
            [Status] IN ('active', 'completed', 'paused', 'abandoned')
        ),
        CONSTRAINT [CK_UserProgramAssignments_CurrentWeek] CHECK ([CurrentWeek] >= 1),
        CONSTRAINT [CK_UserProgramAssignments_CurrentDay] CHECK (
            [CurrentDayOfWeek] >= 0 AND [CurrentDayOfWeek] <= 6
        ),
        CONSTRAINT [UQ_UserProgramAssignments_Active] UNIQUE ([UserId], [ProgramId], [StartDate])
    );
    PRINT 'UserProgramAssignments table created';
END
ELSE
BEGIN
    PRINT 'UserProgramAssignments table already exists';
END

-- Create indexes (idempotent)
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_UserProgramAssignments_UserId' AND object_id = OBJECT_ID('dbo.UserProgramAssignments'))
    CREATE INDEX [IX_UserProgramAssignments_UserId] ON [dbo].[UserProgramAssignments]([UserId]);

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_UserProgramAssignments_ProgramId' AND object_id = OBJECT_ID('dbo.UserProgramAssignments'))
    CREATE INDEX [IX_UserProgramAssignments_ProgramId] ON [dbo].[UserProgramAssignments]([ProgramId]);

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_UserProgramAssignments_UserId_Status' AND object_id = OBJECT_ID('dbo.UserProgramAssignments'))
    CREATE INDEX [IX_UserProgramAssignments_UserId_Status] ON [dbo].[UserProgramAssignments]([UserId], [Status]);

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_UserProgramAssignments_Status' AND object_id = OBJECT_ID('dbo.UserProgramAssignments'))
    CREATE INDEX [IX_UserProgramAssignments_Status] ON [dbo].[UserProgramAssignments]([Status]);
