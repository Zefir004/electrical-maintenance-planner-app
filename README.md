# Планировщик обслуживания электрооборудования

Flask-приложение для планирования осмотров, ремонта и профилактики электрооборудования.

## Что где находится

### Серверная часть

- `app.py` - Flask-маршруты: главная страница, оборудование, задачи, API.
- `database.py` - Функции работы с SQLite и демо-данными.

### Клиентская часть

- `templates/index.html` - HTML-шаблон интерфейса планировщика.
- `static/styles.css` - Стили карточек, форм, статистики и кнопок.

### База данных

- `maintenance.db` - SQLite-база с демо-данными.
- `schema.sql` - SQL-схема таблиц equipment и maintenance_tasks.
- `database.py` - SQL-запросы приложения.

## Отдельные отчёты по заданиям

- `docs/zadanie_2_server.docx` - серверная часть.
- `docs/zadanie_3_client.docx` - клиентская часть.
- `docs/zadanie_4_database.docx` - база данных.

## Запуск

```powershell
pip install -r requirements.txt
python app.py
```
