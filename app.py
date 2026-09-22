"""
Серверная часть на Flask.
Маршруты: главная, добавление оборудования, задачи, смена статуса, JSON API.
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify

import database as db

app = Flask(__name__)


# ---------- ГЛАВНАЯ ----------
@app.route("/")
def index():
    status = request.args.get("status") or None
    search = request.args.get("search") or None

    equipment = db.get_equipment()
    tasks = db.get_tasks(status=status, search=search)

    stats = {
        "equipment": db.count_equipment(),
        "planned": db.count_tasks_by_status("planned"),
        "in_progress": db.count_tasks_by_status("in_progress"),
        "done": db.count_tasks_by_status("done"),
    }

    return render_template(
        "index.html",
        equipment=equipment,
        tasks=tasks,
        stats=stats,
    )


# ---------- ОБОРУДОВАНИЕ ----------
@app.route("/equipment", methods=["POST"])
def add_equipment():
    inventory_number = request.form.get("inventory_number", "").strip()
    name = request.form.get("name", "").strip()
    equipment_type = request.form.get("equipment_type", "").strip()
    location = request.form.get("location", "").strip()
    responsible = request.form.get("responsible", "").strip()

    if inventory_number and name and equipment_type:
        db.add_equipment(inventory_number, name, equipment_type, location, responsible)

    return redirect(url_for("index"))


# ---------- ЗАДАЧИ ----------
@app.route("/tasks", methods=["POST"])
def add_task():
    equipment_id = request.form.get("equipment_id")
    task_type = request.form.get("task_type", "").strip()
    planned_date = request.form.get("planned_date", "").strip()
    priority = request.form.get("priority", "normal").strip() or "normal"
    description = request.form.get("description", "").strip()

    if equipment_id and task_type:
        db.add_task(equipment_id, task_type, planned_date, priority, description)

    return redirect(url_for("index"))


@app.route("/tasks/<int:task_id>/start", methods=["POST"])
def start_task(task_id):
    db.start_task(task_id)
    return redirect(url_for("index"))


@app.route("/tasks/<int:task_id>/complete", methods=["POST"])
def complete_task(task_id):
    db.complete_task(task_id)
    return redirect(url_for("index"))


# ---------- JSON API ----------
@app.route("/api/tasks")
def api_tasks():
    status = request.args.get("status") or None
    search = request.args.get("search") or None

    rows = db.get_tasks(status=status, search=search)
    items = [dict(r) for r in rows]

    return jsonify({"count": len(items), "items": items})


# ---------- ЗАПУСК ----------
if __name__ == "__main__":
    db.init_db()
    app.run(debug=True)