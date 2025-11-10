
USE thalia;

CREATE TABLE IF NOT EXISTS pdf_documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL UNIQUE,
    title VARCHAR(255) NULL, 
    authors VARCHAR(512) NULL,
    journal VARCHAR(500) NULL,
    year INT NULL, 
    doi VARCHAR(255) NULL,
    content LONGTEXT NOT NULL,
    file_path VARCHAR(512),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_indexed_at TIMESTAMP NULL,
    INDEX idx_title (title),
    INDEX idx_authors (authors),
    INDEX idx_year (year)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE users (
    id VARCHAR(50) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    age INT,
    disclaimer_accepted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE user_profiles (
    user_id VARCHAR(50) PRIMARY KEY,
    baseline_completed BOOLEAN DEFAULT FALSE,
    baseline_date DATE,
    baseline_total_score INT,
    baseline_q1 INT,
    baseline_q2 INT,
    baseline_q3 INT,
    baseline_q4 INT,
    baseline_q5 INT,
    baseline_q6 INT,
    baseline_q7 INT,
    baseline_q8 INT,
    baseline_q9 INT,
    baseline_q10 INT,
    baseline_q11 INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CHECK (baseline_q1 BETWEEN 0 AND 4),
    CHECK (baseline_q2 BETWEEN 0 AND 4),
    CHECK (baseline_q3 BETWEEN 0 AND 4),
    CHECK (baseline_q4 BETWEEN 0 AND 4),
    CHECK (baseline_q5 BETWEEN 0 AND 4),
    CHECK (baseline_q6 BETWEEN 0 AND 4),
    CHECK (baseline_q7 BETWEEN 0 AND 4),
    CHECK (baseline_q8 BETWEEN 0 AND 4),
    CHECK (baseline_q9 BETWEEN 0 AND 4),
    CHECK (baseline_q10 BETWEEN 0 AND 4),
    CHECK (baseline_q11 BETWEEN 0 AND 4),
    CHECK (baseline_total_score BETWEEN 0 AND 44)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE mrs_assessments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    assessment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_score INT,
    q1 INT,
    q2 INT,
    q3 INT,
    q4 INT,
    q5 INT,
    q6 INT,
    q7 INT,
    q8 INT,
    q9 INT,
    q10 INT,
    q11 INT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_date (user_id, assessment_date),
    INDEX idx_assessment_date (assessment_date),
    CHECK (q1 BETWEEN 0 AND 4),
    CHECK (q2 BETWEEN 0 AND 4),
    CHECK (q3 BETWEEN 0 AND 4),
    CHECK (q4 BETWEEN 0 AND 4),
    CHECK (q5 BETWEEN 0 AND 4),
    CHECK (q6 BETWEEN 0 AND 4),
    CHECK (q7 BETWEEN 0 AND 4),
    CHECK (q8 BETWEEN 0 AND 4),
    CHECK (q9 BETWEEN 0 AND 4),
    CHECK (q10 BETWEEN 0 AND 4),
    CHECK (q11 BETWEEN 0 AND 4),
    CHECK (total_score BETWEEN 0 AND 44)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE symptom_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    symptom VARCHAR(100) NOT NULL,
    severity INT NOT NULL,
    note TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    timestamp TIMESTAMP NOT NULL,
    confirmed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_timestamp (user_id, timestamp),
    INDEX idx_status (status),
    INDEX idx_user_status (user_id, status),
    INDEX idx_symptom (symptom),
    CHECK (severity BETWEEN 1 AND 3),
    CHECK (status IN ('pending', 'confirmed'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

