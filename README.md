# "" - проект, реализованный с использованием docker-compose

Выполнил: Глазков Никита

## Требования

|   № | Требование                                    | Выполнено ли |
| --: | --------------------------------------------- | :----------: |
|  1. | CRUD                                          |      ❌      |
|  2. | Where с объединением трёх таблиц              |      ❌      |
|  3. | Вложенный select                              |      ❌      |
|  4. | Join                                          |      ❌      |
|  5. | Агрегация                                     |      ❌      |
|  6. | Триггеры, процедуры                           |      ❌      |
|  7. | Красивая структура бд                         |      ❔      |
|  8. | Связанное решение в серверной sql-база данных |      ✅      |
|  9. | Скрипт с запросами                            |      ❌      |
| 10. | Субъективное мнение преподавателя             |      ❔      |
| 11. | Docker                                        |      ✅      |
| 12. | Знания за пределами курса                     |      ✅      |

## Технологии

- Docker
- PostgreSQL
- Flask
- Nginx
- Gunicorn

## Разработка

### Перед началом работы

- В корне проекта необходимо создать файл `.env` по формату `.env.example` и заполнить переменные окружения

### Необходимые команды

`docker compose up --build` - запуск проекта

### TODO

- Подтягивать конфиг
- Спроектировать ERD
- Написать базовый CRUD
- ...
