-- PostgreSQL initialization script for E-commerce Multi-tenant system
-- This script runs when the database container starts for the first time

-- Create database if not exists (PostgreSQL doesn't support IF NOT EXISTS for CREATE DATABASE)
-- The database is created by the POSTGRES_DB environment variable

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Set timezone
SET timezone = 'UTC';

-- Create a user for the application (if different from POSTGRES_USER)
-- DO $$
-- BEGIN
--   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'ecommerce_user') THEN
--     CREATE ROLE ecommerce_user WITH LOGIN PASSWORD 'ecommerce_password';
--   END IF;
-- END
-- $$;

-- Grant privileges
-- GRANT ALL PRIVILEGES ON DATABASE ecommerce TO ecommerce_user;

-- Set default search path
-- ALTER DATABASE ecommerce SET search_path TO public;