-- Create database and user for the Week3 Day2 app
-- Run as a superuser (for example: psql -U postgres -f init_db.sql)

-- Adjust names/passwords as needed
CREATE USER devops_user WITH PASSWORD 'changeme';
CREATE DATABASE devopsbootcamp OWNER devops_user;
GRANT ALL PRIVILEGES ON DATABASE devopsbootcamp TO devops_user;

\c devopsbootcamp

-- Table creation is also handled by the app, but you can create it manually:
CREATE TABLE IF NOT EXISTS students (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  country TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT now()
);
