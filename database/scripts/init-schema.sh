#!/bin/bash
# Database Migration Script
# Applies versioned migrations in order, tracking applied versions in SchemaVersions table

set -e

DB_SERVER="$1"
DB_NAME="$2"
DB_USER="$3"
DB_PASSWORD="$4"
MIGRATIONS_PATH="${5:-database/migrations}"

if [ -z "$DB_SERVER" ] || [ -z "$DB_NAME" ] || [ -z "$DB_USER" ] || [ -z "$DB_PASSWORD" ]; then
    echo "Usage: $0 <server> <database> <user> <password> [migrations_path]"
    exit 1
fi

export SQLCMDPASSWORD="$DB_PASSWORD"

# Common sqlcmd options - use TrustServerCertificate for Azure SQL
SQLCMD_OPTS="-S $DB_SERVER -d $DB_NAME -U $DB_USER -C -b"

echo "================================================"
echo "Database Migration Runner"
echo "Server: $DB_SERVER"
echo "Database: $DB_NAME"
echo "Migrations: $MIGRATIONS_PATH"
echo "================================================"

# Step 1: Ensure SchemaVersions table exists
echo ""
echo "Step 1: Ensuring SchemaVersions table exists..."
sqlcmd $SQLCMD_OPTS -Q "
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
ELSE
BEGIN
    PRINT 'SchemaVersions table already exists';
END
"

# Step 2: Get list of already applied migrations
echo ""
echo "Step 2: Checking applied migrations..."
APPLIED_VERSIONS=$(sqlcmd $SQLCMD_OPTS -h -1 -W -Q "SET NOCOUNT ON; SELECT Version FROM SchemaVersions ORDER BY Version;" 2>/dev/null | tr -d '\r' | grep -v '^$' || true)

echo "Previously applied migrations:"
if [ -z "$APPLIED_VERSIONS" ]; then
    echo "  (none)"
else
    echo "$APPLIED_VERSIONS" | while read version; do
        echo "  - $version"
    done
fi

# Step 3: Apply pending migrations in order
echo ""
echo "Step 3: Applying pending migrations..."
MIGRATIONS_APPLIED=0
MIGRATIONS_SKIPPED=0

for file in $(ls -1 "$MIGRATIONS_PATH"/*.sql 2>/dev/null | sort); do
    if [ -f "$file" ]; then
        # Extract version from filename (e.g., "004" from "004_drop_legacy_tables.sql")
        FILENAME=$(basename "$file")
        VERSION=$(echo "$FILENAME" | sed 's/_.*//' | sed 's/\.sql//')
        DESCRIPTION=$(echo "$FILENAME" | sed 's/^[0-9]*_//' | sed 's/\.sql$//' | tr '_' ' ')
        
        # Skip schema_versions migration since we handle it above
        if [ "$VERSION" = "000" ]; then
            echo "  Skipping $FILENAME (handled internally)"
            continue
        fi
        
        # Check if already applied
        if echo "$APPLIED_VERSIONS" | grep -q "^${VERSION}$"; then
            echo "  Skipping $FILENAME (already applied)"
            MIGRATIONS_SKIPPED=$((MIGRATIONS_SKIPPED + 1))
            continue
        fi
        
        echo "  Applying $FILENAME..."
        START_TIME=$(date +%s%3N)
        
        # Execute migration
        if sqlcmd $SQLCMD_OPTS -i "$file"; then
            END_TIME=$(date +%s%3N)
            EXEC_TIME=$((END_TIME - START_TIME))
            
            # Record successful migration
            sqlcmd $SQLCMD_OPTS -Q "
                INSERT INTO SchemaVersions (Version, Description, ExecutionTimeMs)
                VALUES ('$VERSION', '$DESCRIPTION', $EXEC_TIME);
            "
            echo "    ✓ Applied in ${EXEC_TIME}ms"
            MIGRATIONS_APPLIED=$((MIGRATIONS_APPLIED + 1))
        else
            echo "    ✗ Failed to apply $FILENAME"
            exit 1
        fi
    fi
done

echo ""
echo "================================================"
echo "Migration Summary"
echo "  Applied: $MIGRATIONS_APPLIED"
echo "  Skipped: $MIGRATIONS_SKIPPED (already applied)"
echo "================================================"
echo "✓ Database migration completed successfully!"
