param(
    [Parameter(Mandatory=$true)]
    [string]$ServerName,
    
    [Parameter(Mandatory=$true)]
    [string]$DatabaseName,
    
    [Parameter(Mandatory=$true)]
    [string]$UserId,
    
    [Parameter(Mandatory=$true)]
    [string]$Password,
    
    [string]$MigrationsPath = "./database/migrations"
)

# Set error action preference
$ErrorActionPreference = "Stop"

Write-Host "================================================"
Write-Host "Database Migration Runner"
Write-Host "Server: $ServerName"
Write-Host "Database: $DatabaseName"
Write-Host "Migrations: $MigrationsPath"
Write-Host "================================================"

try {
    # Common parameters for Invoke-Sqlcmd
    $sqlParams = @{
        ServerInstance = $ServerName
        Database = $DatabaseName
        Username = $UserId
        Password = $Password
        TrustServerCertificate = $true
        ErrorAction = "Stop"
    }

    # Step 1: Ensure SchemaVersions table exists
    Write-Host "`nStep 1: Ensuring SchemaVersions table exists..."
    $createSchemaVersions = @"
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'SchemaVersions')
BEGIN
    CREATE TABLE [dbo].[SchemaVersions] (
        [Id] INT PRIMARY KEY IDENTITY(1,1),
        [Version] NVARCHAR(50) NOT NULL UNIQUE,
        [Description] NVARCHAR(255) NOT NULL,
        [AppliedAt] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        [ExecutionTimeMs] BIGINT
    );
    PRINT 'Created SchemaVersions table';
END
"@
    Invoke-Sqlcmd @sqlParams -Query $createSchemaVersions

    # Step 2: Get list of already applied migrations
    Write-Host "`nStep 2: Checking applied migrations..."
    $appliedVersions = Invoke-Sqlcmd @sqlParams -Query "SELECT Version FROM SchemaVersions ORDER BY Version" | 
        ForEach-Object { $_.Version }
    
    Write-Host "Previously applied migrations:"
    if ($appliedVersions.Count -eq 0) {
        Write-Host "  (none)"
    } else {
        $appliedVersions | ForEach-Object { Write-Host "  - $_" }
    }

    # Step 3: Apply pending migrations in order
    Write-Host "`nStep 3: Applying pending migrations..."
    $migrations = Get-ChildItem -Path $MigrationsPath -Filter "*.sql" | Sort-Object Name
    $migrationsApplied = 0
    $migrationsSkipped = 0

    foreach ($migration in $migrations) {
        # Extract version from filename (e.g., "004" from "004_drop_legacy_tables.sql")
        $version = ($migration.BaseName -split '_')[0]
        $description = ($migration.BaseName -replace '^\d+_', '') -replace '_', ' '
        
        # Skip schema_versions migration since we handle it above
        if ($version -eq "000") {
            Write-Host "  Skipping $($migration.Name) (handled internally)"
            continue
        }
        
        # Check if already applied
        if ($appliedVersions -contains $version) {
            Write-Host "  Skipping $($migration.Name) (already applied)"
            $migrationsSkipped++
            continue
        }
        
        Write-Host "  Applying $($migration.Name)..."
        $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
        
        # Execute migration
        $sqlScript = Get-Content -Path $migration.FullName -Raw
        Invoke-Sqlcmd @sqlParams -Query $sqlScript
        
        $stopwatch.Stop()
        $execTimeMs = $stopwatch.ElapsedMilliseconds
        
        # Record successful migration
        $recordMigration = @"
INSERT INTO SchemaVersions (Version, Description, ExecutionTimeMs)
VALUES ('$version', '$description', $execTimeMs);
"@
        Invoke-Sqlcmd @sqlParams -Query $recordMigration
        
        Write-Host "    ✓ Applied in ${execTimeMs}ms"
        $migrationsApplied++
    }

    Write-Host "`n================================================"
    Write-Host "Migration Summary"
    Write-Host "  Applied: $migrationsApplied"
    Write-Host "  Skipped: $migrationsSkipped (already applied)"
    Write-Host "================================================"
    Write-Host "✓ Database migration completed successfully!"
}
catch {
    Write-Error "Database migration failed: $_"
    exit 1
}
