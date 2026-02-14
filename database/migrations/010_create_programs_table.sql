-- Create Programs table
-- Version: 010
-- Created: 2026-02-13
-- Description: Organized groups of workouts forming complete strength programs

IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'Programs')
BEGIN
    CREATE TABLE [dbo].[Programs] (
        [ProgramId] UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        [CreatorId] UNIQUEIDENTIFIER NOT NULL,
        [Name] NVARCHAR(255) NOT NULL,
        [Description] NVARCHAR(MAX),
        [IsShared] BIT NOT NULL DEFAULT 0,
        [DurationWeeks] INT NOT NULL DEFAULT 1,
        [CreatedAt] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        [UpdatedAt] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        CONSTRAINT [FK_Programs_Users] FOREIGN KEY ([CreatorId]) 
            REFERENCES [dbo].[Users]([UserId]) ON DELETE CASCADE
    );

    CREATE INDEX [IX_Programs_CreatorId] ON [dbo].[Programs]([CreatorId]);
    CREATE INDEX [IX_Programs_IsShared] ON [dbo].[Programs]([IsShared]) WHERE [IsShared] = 1;

    PRINT 'Programs table created';
END
ELSE
BEGIN
    PRINT 'Programs table already exists';
END

