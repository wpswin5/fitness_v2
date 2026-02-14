# Database Project

Azure SQL Database infrastructure and migrations for the Fitness API.

## Structure

```
database/
├── migrations/          # Versioned SQL migrations (applied in order)
│   ├── 000_schema_versions.sql   # Migration tracking table (internal)
│   ├── 004_drop_legacy_tables.sql
│   ├── 005_alter_users_table.sql
│   ├── 006_create_exercises_table.sql
│   └── ...
├── schema/
│   ├── tables/          # Reference SQL definitions (generated from migrations)
│   └── DESIGN.md        # Schema design documentation
└── scripts/
    ├── init-schema.sh   # Migration runner (used by CI/CD)
    └── deploy-db.ps1    # PowerShell migration runner (local)
```

## Migration System

Migrations are versioned SQL scripts that are applied in order. The `SchemaVersions` table tracks which migrations have been applied.

### Key Features
- **Idempotent**: Migrations use `IF NOT EXISTS` checks and can safely be re-run
- **Version Tracking**: Applied migrations are recorded in `dbo.SchemaVersions`
- **Ordered Execution**: Scripts are applied in alphabetical/numerical order
- **Atomic Rollback**: If a migration fails, it won't be recorded as applied

### Creating a New Migration

1. Create a new file in `migrations/` with the next version number:
   ```
   015_add_new_feature.sql
   ```

2. Use idempotent patterns:
   ```sql
   IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'NewTable')
   BEGIN
       CREATE TABLE [dbo].[NewTable] (...);
       PRINT 'NewTable created';
   END
   ```

3. Test locally, then commit and push to trigger deployment.

## Local Development

### Run migrations locally (bash):
```bash
./database/scripts/init-schema.sh \
    "localhost" \
    "fitnessdb" \
    "sa" \
    "YourPassword"
```

### Run migrations locally (PowerShell):
```powershell
./database/scripts/deploy-db.ps1 \
    -ServerName "localhost" \
    -DatabaseName "fitnessdb" \
    -UserId "sa" \
    -Password "YourPassword"
```

## CI/CD Deployment

Migrations are automatically applied via GitHub Actions on push to `main`. See [DEPLOYMENT.md](../docs/DEPLOYMENT.md) for details.
