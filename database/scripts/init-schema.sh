#!/bin/bash
# Database Schema Initialization Script
# Applies database schema in correct order: SchemaVersions → Tables → Views → Stored Procedures

set -e

DB_SERVER="$1"
DB_NAME="$2"
DB_USER="$3"
DB_PASSWORD="$4"

if [ -z "$DB_SERVER" ] || [ -z "$DB_NAME" ] || [ -z "$DB_USER" ] || [ -z "$DB_PASSWORD" ]; then
    echo "Usage: $0 <server> <database> <user> <password>"
    exit 1
fi

export SQLCMDPASSWORD="$DB_PASSWORD"

echo "Initializing database schema for: $DB_NAME"

# Step 1: Create SchemaVersions table if it doesn't exist
echo "Step 1: Ensuring SchemaVersions table exists..."
sqlcmd -S "$DB_SERVER" \
       -d "$DB_NAME" \
       -U "$DB_USER" \
       -i "database/migrations/000_schema_versions.sql"

# Step 2: Apply all tables from database/schema/tables/
echo "Step 2: Applying table definitions..."
for file in database/schema/tables/*.sql; do
    if [ -f "$file" ]; then
        echo "  Applying table: $file"
        sqlcmd -S "$DB_SERVER" \
               -d "$DB_NAME" \
               -U "$DB_USER" \
               -i "$file"
    fi
done

# Step 3: Apply all views from database/schema/views/
echo "Step 3: Applying views..."
for file in database/schema/views/*.sql; do
    if [ -f "$file" ]; then
        echo "  Applying view: $file"
        sqlcmd -S "$DB_SERVER" \
               -d "$DB_NAME" \
               -U "$DB_USER" \
               -i "$file"
    fi
done

# Step 4: Apply all stored procedures from database/schema/stored_procedures/
echo "Step 4: Applying stored procedures..."
for file in database/schema/stored_procedures/*.sql; do
    if [ -f "$file" ]; then
        echo "  Applying stored procedure: $file"
        sqlcmd -S "$DB_SERVER" \
               -d "$DB_NAME" \
               -U "$DB_USER" \
               -i "$file"
    fi
done

echo "✓ Database schema initialization completed successfully!"
