-- Alter Users table for Auth0 integration
-- Version: 005
-- Created: 2026-02-13
-- Description: Add Auth0 subject identifier and convert to UNIQUEIDENTIFIER PK

-- Check if migration is needed (old Users table has INT PK)
IF EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('dbo.Users') AND name = 'UserId' AND system_type_id = 56) -- 56 = INT
BEGIN
    PRINT 'Migrating Users table to new schema...';
    
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
    INSERT INTO [dbo].[Users_New] ([Email], [FirstName], [LastName], [CreatedAt], [UpdatedAt], [Auth0Sub])
    SELECT [Email], [FirstName], [LastName], [CreatedAt], [UpdatedAt], 
           'migration_placeholder_' + CAST([UserId] AS NVARCHAR(50))
    FROM [dbo].[Users];

    -- Step 3: Drop old table and rename new one
    DROP TABLE [dbo].[Users];
    EXEC sp_rename 'dbo.Users_New', 'Users';

    -- Create indexes
    IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_Users_Email')
        CREATE INDEX [IX_Users_Email] ON [dbo].[Users]([Email]);
    IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_Users_Auth0Sub')
        CREATE INDEX [IX_Users_Auth0Sub] ON [dbo].[Users]([Auth0Sub]);

    PRINT 'Users table migrated to new schema with Auth0 support';
END
ELSE IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'Users')
BEGIN
    -- Fresh install - create Users table directly
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

    CREATE INDEX [IX_Users_Email] ON [dbo].[Users]([Email]);
    CREATE INDEX [IX_Users_Auth0Sub] ON [dbo].[Users]([Auth0Sub]);

    PRINT 'Users table created (fresh install)';
END
ELSE
BEGIN
    PRINT 'Users table already has correct schema';
END

-- Ensure indexes exist (idempotent fallback)
IF EXISTS (SELECT 1 FROM sys.tables WHERE name = 'Users')
BEGIN
    IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_Users_Email' AND object_id = OBJECT_ID('dbo.Users'))
        CREATE INDEX [IX_Users_Email] ON [dbo].[Users]([Email]);
    
    IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_Users_Auth0Sub' AND object_id = OBJECT_ID('dbo.Users'))
        CREATE INDEX [IX_Users_Auth0Sub] ON [dbo].[Users]([Auth0Sub]);
END