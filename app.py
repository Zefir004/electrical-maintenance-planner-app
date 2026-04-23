from flask import Flask, jsonify, redirect, render_template, request, url_for

from database import (
    add_equipment,
    add_task,
    complete_task,
    get_equipment,
    get_stats,
    get_tasks,
    init_db,
    seed_demo_data,
    start_task,
)


app = Flask(__name__)
init_db()
seed_demo_data()


@app.get("/")
def index():
    status = request.args.get("status", "").strip()
    search = request.args.get("search", "").strip()
    return render_template(
        "index.html",
        equipment=get_equipment(),
        tasks=get_tasks(status or None, search or None),
        stats=get_stats(),
        selected_status=status,
        search=search,
    )


@app.post("/equipment")
def create_equipment():
    add_equipment(
        request.form["inventory_number"].strip(),
        request.form["name"].strip(),
        request.form["equipment_type"].strip(),
        request.form["location"].strip(),
        request.form["responsible"].strip(),
    )
    return redirect(url_for("index"))


@app.post("/tasks")
def create_task():
    add_task(
        int(request.form["equipment_id"]),
        request.form["task_type"].strip(),
        request.form["planned_date"].strip(),
        request.form.get("priority", "normal"),
        request.form["description"].strip(),
    )
    return redirect(url_for("index"))


@app.post("/tasks/<int:task_id>/start")
def start(task_id):
    start_task(task_id)
    return redirect(url_for("index"))


@app.post("/tasks/<int:task_id>/complete")
def complete(task_id):
    complete_task(task_id)
    return redirect(url_for("index"))


@app.get("/api/tasks")
def api_tasks():
    status = request.args.get("status", "").strip()
    search = request.args.get("search", "").strip()
    tasks = get_tasks(status or None, search or None)
    return jsonify({"count": len(tasks), "items": tasks})


if __name__ == "__main__":
    app.run(debug=True)
