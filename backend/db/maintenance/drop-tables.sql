USE thalia;

-- drop event first (optional)
DROP EVENT IF EXISTS cleanup_old_pending_logs;

-- drop child tables
DROP TABLE IF EXISTS symptom_logs;
DROP TABLE IF EXISTS mrs_assessments;
DROP TABLE IF EXISTS user_profiles;

-- drop core tables
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS pdf_documents;
