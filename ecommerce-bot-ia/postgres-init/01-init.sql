-- Crea usuario y DB si no existen
DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'ecommerce_user') THEN
    CREATE USER ecommerce_user WITH PASSWORD 'ecommerce123';
  END IF;
END$$;

DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'ecommerce_multi_tenant') THEN
    CREATE DATABASE ecommerce_multi_tenant;
  END IF;
END$$;

GRANT ALL PRIVILEGES ON DATABASE ecommerce_multi_tenant TO ecommerce_user;

\connect ecommerce_multi_tenant
GRANT USAGE, CREATE ON SCHEMA public TO ecommerce_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO ecommerce_user;