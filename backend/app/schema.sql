--
-- Устанавливаем UTC+3 для БД
SET TIME ZONE 'Europe/Moscow';
ALTER DATABASE misis_project
SET TIMEZONE TO 'Europe/Moscow';
--
-- Таблица пользователей
CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL,
  password VARCHAR(255) NOT NULL
);
--
-- Таблица категорий
CREATE TABLE IF NOT EXISTS categories (
  id SERIAL PRIMARY KEY,
  category_name VARCHAR(255) NOT NULL,
  parent_category_id INTEGER REFERENCES categories(id) ON DELETE RESTRICT ON UPDATE CASCADE
);
--
-- Таблица рецептов
CREATE TABLE IF NOT EXISTS receipts (
  id SERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  category_id INTEGER REFERENCES categories(id) ON DELETE RESTRICT ON UPDATE CASCADE,
  author_id INTEGER REFERENCES users(id) ON DELETE RESTRICT ON UPDATE CASCADE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT NOW()
);
--
-- Таблица ингредиентов
CREATE TABLE IF NOT EXISTS ingredients (
  id SERIAL PRIMARY KEY,
  ingredient_name VARCHAR(255) NOT NULL
);
--
-- Таблица единиц измерения
CREATE TABLE IF NOT EXISTS units (
  id SERIAL PRIMARY KEY,
  short_name VARCHAR(255) NOT NULL,
  full_name VARCHAR(255) NOT NULL
);
--
-- Таблица ингредиентов в рецептах
CREATE TABLE IF NOT EXISTS ingredients_in_receipts (
  id SERIAL PRIMARY KEY,
  ingredient_id INTEGER REFERENCES ingredients(id) ON DELETE RESTRICT ON UPDATE CASCADE,
  receipt_id INTEGER REFERENCES receipts(id) ON DELETE RESTRICT ON UPDATE CASCADE,
  unit_id INTEGER REFERENCES units(id) ON DELETE RESTRICT ON UPDATE CASCADE,
  amount INTEGER NOT NULL,
  comment VARCHAR(255)
);
-- Добавляем проверку на то, чтобы количество ингридиента было больше 0, если она уже не существует
DO $$ BEGIN IF NOT EXISTS (
  SELECT 1
  FROM information_schema.table_constraints
  WHERE constraint_name = 'min_amount'
    AND table_name = 'ingredients_in_receipts'
) THEN
ALTER TABLE ingredients_in_receipts
ADD CONSTRAINT min_amount CHECK (amount >= 0);
END IF;
END $$;
--
-- Триггер для фиксации даты и времени обновления
CREATE OR REPLACE FUNCTION set_updated_at() RETURNS TRIGGER AS $$ BEGIN NEW.updated_at = NOW();
RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE OR REPLACE TRIGGER set_receipts_updated_at BEFORE
UPDATE ON receipts FOR EACH ROW EXECUTE PROCEDURE set_updated_at();
--
-- -- TODO Запрос для получения цепочки до родительской категории
-- WITH RECURSIVE category_chain (id, category_name, parent_category_id) AS (
--   SELECT id,
--     category_name,
--     parent_category_id
--   FROM categories
--   WHERE id = 2
--   UNION ALL
--   SELECT c.id,
--     c.category_name,
--     c.parent_category_id
--   FROM categories c
--     JOIN category_chain cc ON cc.parent_category_id = c.id
-- )
-- SELECT *
-- FROM category_chain;