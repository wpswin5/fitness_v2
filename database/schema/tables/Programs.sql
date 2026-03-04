-- Programs Table
-- Organized groups of workouts forming complete strength programs

CREATE TABLE [dbo].[Programs] (
    [ProgramId] UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    [CreatorId] UNIQUEIDENTIFIER NOT NULL,
    [Name] NVARCHAR(255) NOT NULL,
    [Description] NVARCHAR(MAX),
    [IsShared] BIT NOT NULL DEFAULT 0,
    [DurationWeeks] INT NOT NULL DEFAULT 1,
    [DeletedAt] DATETIME2 NULL, -- Soft delete: NULL = active, non-null = deleted
    [CreatedAt] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    [UpdatedAt] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    CONSTRAINT [FK_Programs_Users] FOREIGN KEY ([CreatorId]) 
        REFERENCES [dbo].[Users]([UserId]) ON DELETE CASCADE
);

-- Create indexes
CREATE INDEX [IX_Programs_CreatorId] ON [dbo].[Programs]([CreatorId]);
CREATE INDEX [IX_Programs_IsShared] ON [dbo].[Programs]([IsShared]);
CREATE INDEX [IX_Programs_DeletedAt] ON [dbo].[Programs]([DeletedAt]);
CREATE INDEX [IX_Programs_Active_CreatorId] ON [dbo].[Programs]([CreatorId]) WHERE [DeletedAt] IS NULL;
CREATE INDEX [IX_Programs_Active_Shared] ON [dbo].[Programs]([IsShared]) WHERE [DeletedAt] IS NULL AND [IsShared] = 1;
