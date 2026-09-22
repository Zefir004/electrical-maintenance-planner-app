"""
Модуль работы с SQLite.
Все SQL-запросы вынесены сюда, чтобы app.py не работал с базой напрямую.
"""

import os
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "maintenance.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")


# ---------- СОЕДИНЕНИЕ ----------
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ---------- ИНИЦИАЛИЗАЦИЯ ----------
def init_db():
    first_run = not os.path.exists(DB_PATH)
    conn = get_connection()
    cur = conn.cursor()

    if first_run:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            cur.executescript(f.read())
        conn.commit()
        _insert_demo_data(conn)
        print("[db] База данных создана и заполнена демо-данными.")
    else:
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='equipment'"
        )
        if cur.fetchone() is None:
            with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
                cur.executescript(f.read())
            conn.commit()
            _insert_demo_data(conn)
            print("[db] Таблицы пересозданы.")

    conn.close()


def _insert_demo_data(conn):
    cur = conn.cursor()

    equipment = [
        # inventory_number, name, equipment_type, location, responsible, status
        ("EQ-001", "Трансформатор ТМ-250", "Трансформатор", "Подстанция 1", "Иванов И.И.", "active"),
        ("EQ-002", "Распределительный щит ЩР-12", "Щит", "Цех 2", "Петров П.П.", "service"),
        ("EQ-003", "Дизель-генератор 40 кВт", "Генератор", "Резервный блок", "Сидоров С.С.", "active"),
    ]
    cur.executemany(
        """INSERT INTO equipment
           (inventory_number, name, equipment_type, location, responsible, status)
           VALUES (?, ?, ?, ?, ?, ?)""",
        equipment,
    )

    tasks = [
        # equipment_id, task_type, planned_date, priority, description, status, completed_at
        (1, "Плановый осмотр", "2026-04-28", "normal",
         "Проверить нагрев, уровень масла и контактные соединения", "planned", None),
        (2, "Ремонт", "2026-04-24", "high",
         "Заменить автоматический выключатель", "in_progress", None),
        (3, "Тестовый запуск", "2026-05-05", "low",
         "Проверить запуск под нагрузкой", "planned", None),
    ]
    cur.executemany(
        """INSERT INTO maintenance_tasks
           (equipment_id, task_type, planned_date, priority, description, status, completed_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        tasks,
    )
    conn.commit()


# ---------- ОБОРУДОВАНИЕ ----------
def get_equipment():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM equipment ORDER BY inventory_number"
    ).fetchall()
    conn.close()
    return rows


def add_equipment(inventory_number, name, equipment_type, location, responsible):
    conn = get_connection()
    conn.execute(
        """INSERT INTO equipment
           (inventory_number, name, equipment_type, location, responsible, status)
           VALUES (?, ?, ?, ?, ?, 'active')""",
        (inventory_number, name, equipment_type, location, responsible),
    )
    conn.commit()
    conn.close()


def count_equipment():
    conn = get_connection()
    n = conn.execute("SELECT COUNT(*) FROM equipment").fetchone()[0]
    conn.close()
    return n


# ---------- ЗАДАЧИ ----------
def get_tasks(status=None, search=None):
    """
    Возвращает задачи вместе с данными оборудования.
    Фильтрует по статусу и поисковой строке (по номеру, названию или описанию).
    """
    query = """
        SELECT
            maintenance_tasks.id             AS id,
            equipment.inventory_number       AS inventory_number,
            equipment.name                   AS equipment_name,
            equipment.equipment_type         AS equipment_type,
            equipment.location               AS location,
            equipment.responsible            AS responsible,
            maintenance_tasks.task_type      AS task_type,
            maintenance_tasks.planned_date   AS planned_date,
            maintenance_tasks.priority       AS priority,
            maintenance_tasks.description    AS description,
            maintenance_tasks.status         AS status,
            maintenance_tasks.completed_at   AS completed_at
        FROM maintenance_tasks
        JOIN equipment ON equipment.id = maintenance_tasks.equipment_id
        WHERE 1 = 1
    """
    params = []

    if status:
        query += " AND maintenance_tasks.status = ?"
        params.append(status)

    if search:
        query += """ AND (
            equipment.inventory_number LIKE ? OR
            equipment.name LIKE ? OR
            maintenance_tasks.description LIKE ?
        )"""
        like = f"%{search}%"
        params.extend([like, like, like])

    query += """
        ORDER BY
            CASE maintenance_tasks.status
                WHEN 'in_progress' THEN 1
                WHEN 'planned'     THEN 2
                WHEN 'done'        THEN 3
                ELSE 4
            END,
            maintenance_tasks.planned_date
    """

    conn = get_connection()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows


def add_task(equipment_id, task_type, planned_date, priority, description):
    conn = get_connection()
    conn.execute(
        """INSERT INTO maintenance_tasks
           (equipment_id, task_type, planned_date, priority, description, status)
           VALUES (?, ?, ?, ?, ?, 'planned')""",
        (int(equipment_id), task_type, planned_date, priority, description),
    )
    conn.commit()
    conn.close()


def start_task(task_id):
    """Переводит задачу в статус in_progress."""
    conn = get_connection()
    conn.execute(
        "UPDATE maintenance_tasks SET status = 'in_progress' WHERE id = ?",
        (int(task_id),),
    )
    conn.commit()
    conn.close()


def complete_task(task_id):
    """Отмечает задачу выполненной, записывает дату завершения."""
    conn = get_connection()
    conn.execute(
        """UPDATE maintenance_tasks
           SET status = 'done', completed_at = ?
           WHERE id = ?""",
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), int(task_id)),
    )
    conn.commit()
    conn.close()


def count_tasks_by_status(status):
    conn = get_connection()
    n = conn.execute(
        "SELECT COUNT(*) FROM maintenance_tasks WHERE status = ?", (status,)
    ).fetchone()[0]
    conn.close()
    return n