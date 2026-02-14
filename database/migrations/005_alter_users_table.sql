-- Alter Users table for Auth0 integration
-- Version: 005
-- Created: 2026-02-13
-- Description: Add Auth0 subject identifier and convert to UNIQUEIDENTIFIER PK

-- Step 1: Create new Users table with proper schema
CREATE TABLE [dbo].[Users_New] (
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

-- Step 2: Migrate existing data (if any)
-- Note: Auth0Sub will need to be populated separately for existing users
INSERT INTO [dbo].[Users_New] ([Email], [FirstName], [LastName], [CreatedAt], [UpdatedAt], [Auth0Sub])
SELECT [Email], [FirstName], [LastName], [CreatedAt], [UpdatedAt], 
       'migration_placeholder_' + CAST([UserId] AS NVARCHAR(50)) -- Placeholder until Auth0 sync
FROM [dbo].[Users];

-- Step 3: Drop old table and rename new one
DROP TABLE [dbo].[Users];

EXEC sp_rename 'dbo.Users_New', 'Users';
EXEC sp_rename 'dbo.UQ_Users_Auth0Sub', 'UQ_Users_Auth0Sub', 'OBJECT';
EXEC sp_rename 'dbo.UQ_Users_Email', 'UQ_Users_Email', 'OBJECT';

-- Create indexes
CREATE INDEX [IX_Users_Email] ON [dbo].[Users]([Email]);
CREATE INDEX [IX_Users_Auth0Sub] ON [dbo].[Users]([Auth0Sub]);

PRINT 'Users table migrated to new schema with Auth0 support';

