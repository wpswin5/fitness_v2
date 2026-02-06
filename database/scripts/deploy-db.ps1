param(
    [Parameter(Mandatory=$true)]
    [string]$ServerName,
    
    [Parameter(Mandatory=$true)]
    [string]$DatabaseName,
    
    [Parameter(Mandatory=$true)]
    [string]$UserId,
    
    [Parameter(Mandatory=$true)]
    [string]$Password,
    
    [string]$MigrationsPath = "./migrations"
)

# Set error action preference
$ErrorActionPreference = "Stop"

Write-Host "Starting database deployment..."
Write-Host "Server: $ServerName"
Write-Host "Database: $DatabaseName"

try {
    # Connection string
    $connectionString = "Server=$ServerName;Initial Catalog=$DatabaseName;User ID=$UserId;Password=$Password;"
    
    # Get all migration files in order
    $migrations = Get-ChildItem -Path $MigrationsPath -Filter "*.sql" | Sort-Object Name
    
    Write-Host "Found $($migrations.Count) migration files"
    
    foreach ($migration in $migrations) {
        Write-Host "Applying migration: $($migration.Name)"
        
        $sqlScript = Get-Content -Path $migration.FullName -Raw
        
        # Execute script
        Invoke-Sqlcmd -ServerInstance $ServerName `
                      -Database $DatabaseName `
                      -Username $UserId `
                      -Password $Password `
                      -Query $sqlScript `
                      -ErrorAction Stop
        
        Write-Host "✓ Migration $($migration.Name) completed"
    }
    
    Write-Host "Database deployment completed successfully!"
}
catch {
    Write-Error "Database deployment failed: $_"
    exit 1
}
