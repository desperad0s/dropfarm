# Supabase Database Approach

This document outlines our approach for database management using Supabase in our project.

## Current Approach
We are using Supabase for both authentication and data storage. This approach allows for quick iteration during the development phase while providing scalability for future growth.

## Handling Schema Changes

When you need to change your data model:

1. Update the corresponding Pydantic model in `models.py`.
2. Use Supabase's dashboard to modify the table structure:
   - Go to the Supabase project dashboard
   - Navigate to the "Table Editor" section
   - Select the table you want to modify
   - Use the interface to add, remove, or modify columns

3. Update any affected routes or tasks to work with the new structure.

## Best Practices

1. Version Control: Keep your Pydantic models in version control to track changes over time.
2. Testing: After making schema changes, thoroughly test all affected API endpoints and functions.
3. Migrations: For significant changes, consider using Supabase migrations to manage schema updates across environments.

## Data Backup

Regularly backup your Supabase data, especially before making significant schema changes:
- Use Supabase's dashboard to create backups
- Consider implementing automated backups for production environments

## Security

Implement Row Level Security (RLS) policies in Supabase to secure your data as you develop.

## Future Considerations

1. As the project grows, monitor performance and consider optimizing queries and indexes.
2. Implement proper error handling for database operations in your application code.
3. Consider implementing a change management process for database schema updates as the project matures.

# Future Database Structure for Dropfarm

As Dropfarm evolves, we plan to implement a more robust database structure to support advanced features and improve performance. Here's an overview of the planned database schema:

## Users Table
- id (UUID, primary key)
- email (string, unique)
- password_hash (string)
- created_at (timestamp)
- last_login (timestamp)

## Routines Table
- id (UUID, primary key)
- user_id (UUID, foreign key to Users)
- name (string)
- steps (JSON)
- tokens_per_run (integer)
- created_at (timestamp)
- updated_at (timestamp)

## RoutineRuns Table
- id (UUID, primary key)
- routine_id (UUID, foreign key to Routines)
- start_time (timestamp)
- end_time (timestamp)
- status (enum: 'success', 'failure', 'partial')
- tokens_earned (integer)

## UserStats Table
- user_id (UUID, foreign key to Users)
- total_routine_runs (integer)
- total_tokens_earned (integer)
- last_run_date (timestamp)

## AirdropProjects Table
- id (UUID, primary key)
- name (string)
- description (text)
- start_date (date)
- end_date (date)
- total_token_allocation (integer)

## UserAirdropParticipation Table
- id (UUID, primary key)
- user_id (UUID, foreign key to Users)
- project_id (UUID, foreign key to AirdropProjects)
- tokens_earned (integer)
- participation_date (timestamp)

## Improvements and Benefits

1. **Data Integrity**: Foreign key relationships ensure data consistency across tables.
2. **Performance**: Indexed fields for frequently queried data improve query speed.
3. **Scalability**: Separate tables for different entities allow for easier scaling and maintenance.
4. **Analytics**: The structure supports advanced analytics on user performance and airdrop participation.
5. **Audit Trail**: Timestamps and detailed run information provide a comprehensive history of activities.

## Implementation Plan

1. Design the new schema in detail, including all fields, constraints, and indexes.
2. Create a migration plan to move data from the current structure to the new schema.
3. Update the backend API to work with the new database structure.
4. Modify the frontend to utilize any new data or features enabled by the new structure.
5. Implement the changes in a staging environment for thorough testing.
6. Plan and execute the migration of the production database with minimal downtime.

This enhanced database structure will provide a solid foundation for Dropfarm's growth, enabling new features and improving overall system performance and reliability.