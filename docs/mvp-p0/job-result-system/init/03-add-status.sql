USE job_result_db;

-- Add status column if it doesn't exist
-- Note: MySQL doesn't support "IF NOT EXISTS" for ADD COLUMN directly in all versions, 
-- but we can use a procedure or just let it fail if it exists (application logic handles it too).
-- For this script, we assume it's run manually to migrate.

ALTER TABLE job_results 
ADD COLUMN status VARCHAR(20) DEFAULT 'pending' 
AFTER job_id;
