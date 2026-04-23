import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).with_name("maintenance.db")
SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS equipment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    inventory_number TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    equipment_type TEXT NOT NULL,
    location TEXT NOT NULL,
    responsible TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'service', 'stopped')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS maintenance_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_id INTEGER NOT NULL,
    task_type TEXT NOT NULL,
    planned_date TEXT NOT NULL,
    priority TEXT NOT NULL DEFAULT 'normal'
        CHECK (priority IN ('low', 'normal', 'high')),
    description TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'planned'
        CHECK (status IN ('planned', 'in_progress', 'done')),
    completed_at TEXT,
    FOREIGN KEY (equipment_id) REFERENCES equipment(id) ON DELETE CASCADE
);
"""


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():
    with get_connection() as connection:
        connection.executescript(SCHEMA_SQL)


def seed_demo_data():
    with get_connection() as connection:
        count = connection.execute("SELECT COUNT(*) FROM equipment").fetchone()[0]
        if count:
            return
        connection.executemany(
            """
            INSERT INTO equipment
                (inventory_number, name, equipment_type, location, responsible, status)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                ("EQ-001", "Трансформатор ТМ-250", "трансформатор", "подстанция 1", "Петров П.П.", "active"),
                ("EQ-002", "Распределительный щит ЩР-12", "щит", "цех 2", "Сидоров С.С.", "service"),
                ("EQ-003", "Дизель-генератор 40 кВт", "генератор", "резервный блок", "Иванов И.И.", "active"),
            ],
        )
        connection.executemany(
            """
            INSERT INTO maintenance_tasks
                (equipment_id, task_type, planned_date, priority, description, status)
            VALUES ((SELECT id FROM equipment WHERE inventory_number = ?), ?, ?, ?, ?, ?)
            """,
            [
                ("EQ-001", "Плановый осмотр", "2026-04-28", "normal", "Проверить нагрев, уровень масла и контактные соединения", "planned"),
                ("EQ-002", "Ремонт", "2026-04-24", "high", "Заменить автоматический выключатель", "in_progress"),
                ("EQ-003", "Тестовый запуск", "2026-05-05", "low", "Проверить запуск под нагрузкой", "planned"),
            ],
        )


def get_stats():
    with get_connection() as connection:
        total_equipment = connection.execute("SELECT COUNT(*) FROM equipment").fetchone()[0]
        planned = connection.execute("SELECT COUNT(*) FROM maintenance_tasks WHERE status = 'planned'").fetchone()[0]
        in_progress = connection.execute("SELECT COUNT(*) FROM maintenance_tasks WHERE status = 'in_progress'").fetchone()[0]
        done = connection.execute("SELECT COUNT(*) FROM maintenance_tasks WHERE status = 'done'").fetchone()[0]
        return {"equipment": total_equipment, "planned": planned, "in_progress": in_progress, "done": done}


def get_equipment():
    with get_connection() as connection:
        rows = connection.execute("SELECT * FROM equipment ORDER BY id DESC").fetchall()
        return [dict(row) for row in rows]


def add_equipment(inventory_number, name, equipment_type, location, responsible):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO equipment
                (inventory_number, name, equipment_type, location, responsible)
            VALUES (?, ?, ?, ?, ?)
            """,
            (inventory_number, name, equipment_type, location, responsible),
        )
        return cursor.lastrowid


def get_tasks(status=None, search=None):
    query = """
        SELECT
            maintenance_tasks.*,
            equipment.inventory_number,
            equipment.name,
            equipment.location
        FROM maintenance_tasks
        JOIN equipment ON equipment.id = maintenance_tasks.equipment_id
    """
    conditions = []
    params = []
    if status:
        conditions.append("maintenance_tasks.status = ?")
        params.append(status)
    if search:
        conditions.append("(equipment.name LIKE ? OR equipment.inventory_number LIKE ? OR maintenance_tasks.description LIKE ?)")
        value = f"%{search}%"
        params.extend([value, value, value])
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY planned_date ASC, maintenance_tasks.id DESC"
    with get_connection() as connection:
        rows = connection.execute(query, params).fetchall()
        return [dict(row) for row in rows]


def add_task(equipment_id, task_type, planned_date, priority, description):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO maintenance_tasks
                (equipment_id, task_type, planned_date, priority, description)
            VALUES (?, ?, ?, ?, ?)
            """,
            (equipment_id, task_type, planned_date, priority, description),
        )
        return cursor.lastrowid


def start_task(task_id):
    with get_connection() as connection:
        connection.execute("UPDATE maintenance_tasks SET status = 'in_progress' WHERE id = ?", (task_id,))


def complete_task(task_id):
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE maintenance_tasks
            SET status = 'done', completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (task_id,),
        )
