-- Схема БД для планировщика обслуживания электрооборудования

DROP TABLE IF EXISTS maintenance_tasks;
DROP TABLE IF EXISTS equipment;

CREATE TABLE equipment (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    inventory_number TEXT NOT NULL UNIQUE,
    name             TEXT NOT NULL,
    equipment_type   TEXT NOT NULL,
    location         TEXT,
    responsible      TEXT,
    status           TEXT NOT NULL DEFAULT 'active'
                     CHECK (status IN ('active', 'service', 'stopped'))
);

CREATE TABLE maintenance_tasks (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_id  INTEGER NOT NULL,
    task_type     TEXT NOT NULL,
    planned_date  TEXT,
    priority      TEXT NOT NULL DEFAULT 'normal'
                  CHECK (priority IN ('low', 'normal', 'high')),
    description   TEXT,
    status        TEXT NOT NULL DEFAULT 'planned'
                  CHECK (status IN ('planned', 'in_progress', 'done')),
    completed_at  TEXT,
    FOREIGN KEY (equipment_id) REFERENCES equipment(id) ON DELETE CASCADE
);