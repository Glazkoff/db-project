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
-- Таблица рецептов 
CREATE TABLE IF NOT EXISTS receipts (
  id SERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  category_id INTEGER REFERENCES categories(category_id),
  author_id INTEGER REFERENCES users(author_id),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT NOW()
);
-- 
-- Таблица категорий
CREATE TABLE IF NOT EXISTS categories (
  id SERIAL PRIMARY KEY,
  category_name VARCHAR(255) NOT NULL,
  parent_category_id INTEGER REFERENCES categories(id)
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
  unit_name VARCHAR(255) NOT NULL -- ? Минимальное значение
);
-- 
-- Таблица ингредиентов в рецептах
CREATE TABLE IF NOT EXISTS ingredients_in_receipts (
  id SERIAL PRIMARY KEY,
  ingredient_id INTEGER REFERENCES ingredients(id),
  receipt_id INTEGER REFERENCES receipts(id),
  unit_id INTEGER REFERENCES units(id),
  amount INTEGER NOT NULL,
  comment VARCHAR(255)
);
-- Добавляем проверку на то, чтобы количество ингридиента было больше 0
ALTER TABLE ingredients_in_receipts
ADD CONSTRAINT min_amount CHECK (amount >= 0);
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