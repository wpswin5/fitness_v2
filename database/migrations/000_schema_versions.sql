-- Create migration history table
CREATE TABLE [dbo].[SchemaVersions] (
    [Id] INT PRIMARY KEY IDENTITY(1,1),
    [Version] NVARCHAR(50) NOT NULL UNIQUE,
    [Description] NVARCHAR(255) NOT NULL,
    [AppliedAt] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    [ExecutionTimeMs] BIGINT
);
