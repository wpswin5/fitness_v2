-- UserProgramAssignments Table
-- Tracks user enrollment in training programs with progress state

CREATE TABLE [dbo].[UserProgramAssignments] (
    [AssignmentId] UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    [UserId] UNIQUEIDENTIFIER NOT NULL,
    [ProgramId] UNIQUEIDENTIFIER NOT NULL,
    [StartDate] DATE NOT NULL,
    [Status] NVARCHAR(20) NOT NULL DEFAULT 'active', -- active, completed, paused, abandoned
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

-- Create indexes
CREATE INDEX [IX_UserProgramAssignments_UserId] ON [dbo].[UserProgramAssignments]([UserId]);
CREATE INDEX [IX_UserProgramAssignments_ProgramId] ON [dbo].[UserProgramAssignments]([ProgramId]);
CREATE INDEX [IX_UserProgramAssignments_UserId_Status] ON [dbo].[UserProgramAssignments]([UserId], [Status]);
CREATE INDEX [IX_UserProgramAssignments_Status] ON [dbo].[UserProgramAssignments]([Status]);
