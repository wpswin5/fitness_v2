-- Users Table
-- Stores user account information with Auth0 integration

CREATE TABLE [dbo].[Users] (
    [UserId] UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    [Auth0Sub] NVARCHAR(255) NOT NULL,
    [Email] NVARCHAR(255) NOT NULL,
    [FirstName] NVARCHAR(100),
    [LastName] NVARCHAR(100),
    [CreatedAt] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    [UpdatedAt] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    CONSTRAINT [UQ_Users_Auth0Sub] UNIQUE ([Auth0Sub]),
    CONSTRAINT [UQ_Users_Email] UNIQUE ([Email])
);

-- Create indexes
CREATE INDEX [IX_Users_Email] ON [dbo].[Users]([Email]);
CREATE INDEX [IX_Users_Auth0Sub] ON [dbo].[Users]([Auth0Sub]);
