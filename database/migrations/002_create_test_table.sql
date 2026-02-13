-- Create Test table
-- Version: 003
-- Created: 2026-02-12

CREATE TABLE [dbo].[Test] (
    [Id] INT PRIMARY KEY IDENTITY(1,1),
    [Name] NVARCHAR(255) NOT NULL,
    [Description] NVARCHAR(MAX),
    [CreatedAt] DATETIME2 NOT NULL DEFAULT GETUTCDATE()
);

-- Insert sample data
INSERT INTO [dbo].[Test] (Name, Description) VALUES 
('Sample 1', 'This is the first test record'),
('Sample 2', 'This is the second test record'),
('Sample 3', 'This is the third test record');
