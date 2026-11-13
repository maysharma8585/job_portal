CREATE DATABASE IF NOT EXISTS job_portal_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE job_portal_db;

CREATE TABLE IF NOT EXISTS users (
  user_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  full_name VARCHAR(120) NOT NULL,
  email VARCHAR(254) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  role ENUM('job_seeker','employer','admin') NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (user_id), UNIQUE KEY uq_users_email (email),
  KEY idx_users_role_active (role, is_active)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS job_seeker_profiles (
  profile_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id BIGINT UNSIGNED NOT NULL,
  phone VARCHAR(32), skills TEXT, education TEXT, experience TEXT,
  resume_path VARCHAR(500), updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (profile_id), UNIQUE KEY uq_seeker_profile_user (user_id),
  CONSTRAINT fk_seeker_profile_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS companies (
  company_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  owner_user_id BIGINT UNSIGNED NOT NULL,
  company_name VARCHAR(160) NOT NULL, industry VARCHAR(120), location VARCHAR(160),
  website VARCHAR(300), description TEXT,
  PRIMARY KEY (company_id), UNIQUE KEY uq_company_owner (owner_user_id),
  CONSTRAINT fk_company_owner FOREIGN KEY (owner_user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS jobs (
  job_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  company_id BIGINT UNSIGNED NOT NULL,
  title VARCHAR(180) NOT NULL, category VARCHAR(120) NOT NULL,
  description TEXT NOT NULL, requirements TEXT,
  location VARCHAR(160) NOT NULL,
  employment_type ENUM('Full-time','Part-time','Contract','Internship','Temporary') NOT NULL,
  salary_min DECIMAL(12,2), salary_max DECIMAL(12,2), deadline DATE,
  status ENUM('open','closed','removed') NOT NULL DEFAULT 'open',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (job_id), KEY idx_jobs_status_date (status, created_at),
  KEY idx_jobs_company (company_id), KEY idx_jobs_location_type (location, employment_type),
  CONSTRAINT fk_job_company FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE RESTRICT,
  CONSTRAINT chk_job_salary CHECK (salary_min IS NULL OR salary_max IS NULL OR salary_min <= salary_max)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS applications (
  application_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  job_id BIGINT UNSIGNED NOT NULL, job_seeker_id BIGINT UNSIGNED NOT NULL,
  cover_letter TEXT, resume_path VARCHAR(500),
  status ENUM('Pending','Shortlisted','Rejected','Hired','Withdrawn') NOT NULL DEFAULT 'Pending',
  applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (application_id),
  UNIQUE KEY uq_application_job_seeker (job_id, job_seeker_id),
  KEY idx_applications_seeker_date (job_seeker_id, applied_at),
  KEY idx_applications_status (status),
  CONSTRAINT fk_application_job FOREIGN KEY (job_id) REFERENCES jobs(job_id) ON DELETE RESTRICT,
  CONSTRAINT fk_application_seeker FOREIGN KEY (job_seeker_id) REFERENCES users(user_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- Deliberately no seeded accounts, passwords, or fabricated job listings.
