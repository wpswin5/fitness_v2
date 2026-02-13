-- Schema Documentation
# Database Schema

## Tables

### Users
Stores user account information
- File: `tables/Users.sql`

### Workouts
Stores workout/exercise logs for users with references to users
- File: `tables/Workouts.sql`

### Test
Validation table for testing database connectivity
- File: `tables/Test.sql`

## Views
(To be added as needed)

## Stored Procedures
(To be added as needed)

## Notes
- All tables include audit timestamps (CreatedAt, UpdatedAt)
- Foreign key constraints enforce referential integrity
- Indexes are created on commonly queried columns
