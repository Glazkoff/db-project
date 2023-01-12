--
-- Setting UTC + 3 for the database
SET TIME ZONE 'Europe/Moscow';
ALTER DATABASE misis_project
SET TIMEZONE TO 'Europe/Moscow';
--
-- User Table
CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL,
  password VARCHAR(255) NOT NULL
);
--
-- Recipes category table
CREATE TABLE IF NOT EXISTS categories (
  id SERIAL PRIMARY KEY,
  category_name VARCHAR(255) NOT NULL,
  parent_category_id INTEGER REFERENCES categories(id) ON DELETE
  SET NULL ON UPDATE CASCADE
);
--
-- Recipe table
CREATE TABLE IF NOT EXISTS receipts (
  id SERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  category_id INTEGER REFERENCES categories(id) ON DELETE
  SET NULL ON UPDATE CASCADE,
    author_id INTEGER REFERENCES users(id) ON DELETE
  SET NULL ON UPDATE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT NOW()
);
--
-- Ingredients table
CREATE TABLE IF NOT EXISTS ingredients (
  id SERIAL PRIMARY KEY,
  ingredient_name VARCHAR(255) NOT NULL
);
--
-- Units table
CREATE TABLE IF NOT EXISTS units (
  id SERIAL PRIMARY KEY,
  short_name VARCHAR(255) NOT NULL,
  full_name VARCHAR(255) NOT NULL
);
--
-- Ingredients in recipes table
CREATE TABLE IF NOT EXISTS ingredients_in_receipts (
  id SERIAL PRIMARY KEY,
  ingredient_id INTEGER REFERENCES ingredients(id) ON DELETE
  SET NULL ON UPDATE CASCADE,
    receipt_id INTEGER REFERENCES receipts(id) ON DELETE
  SET NULL ON UPDATE CASCADE,
    unit_id INTEGER REFERENCES units(id) ON DELETE
  SET NULL ON UPDATE CASCADE,
    amount INTEGER NOT NULL,
    comment VARCHAR(255)
);
-- Add a check that the quantity of the ingredient is greater than 0 if it does not already exist
DO $$ BEGIN IF NOT EXISTS (
  SELECT 1
  FROM information_schema.table_constraints
  WHERE constraint_name = 'min_amount'
    AND table_name = 'ingredients_in_receipts'
) THEN
ALTER TABLE ingredients_in_receipts
ADD CONSTRAINT min_amount CHECK (amount > 0);
END IF;
END $$;
--
-- Trigger for fixing the date
and time of the
update
CREATE OR REPLACE FUNCTION set_updated_at() RETURNS TRIGGER AS $$ BEGIN NEW.updated_at = NOW();
RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE OR REPLACE TRIGGER set_receipts_updated_at BEFORE
UPDATE ON receipts FOR EACH ROW EXECUTE PROCEDURE set_updated_at();