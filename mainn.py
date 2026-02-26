"""
main.py
-------
FastAPI Task Management System (Beginner Friendly)

What this API does:
- Create, read, update, and delete tasks
- Filter tasks by completion status
- Delete all tasks
- Show task statistics
- Persist tasks in a plain text file (tasks.txt) using JSON Lines:
  one task per line as a JSON object.

Run it:
    uvicorn main:app --reload

Open docs:
    http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import os

# ----------------------------
# App + File Configuration
# ----------------------------

app = FastAPI(
    title="Task Management System",
    description="A simple FastAPI backend to manage tasks stored in a text file (JSON Lines).",
    version="1.0.0",
)

FILE_NAME = "tasks.txt"


# ----------------------------
# Pydantic Models (Validation)
# ----------------------------

class Task(BaseModel):
    """A full task (what we store + return)."""
    id: int
    title: str
    description: str | None = None
    completed: bool = False


class TaskCreate(BaseModel):
    """Data needed to create a task (no ID because we generate it)."""
    title: str
    description: str | None = None


class TaskUpdate(BaseModel):
    """Data allowed when updating a task (all optional)."""
    title: str | None = None
    description: str | None = None
    completed: bool | None = None


# ----------------------------
# File Helpers (JSON Lines)
# ----------------------------

def load_tasks() -> list[dict]:
    """
    Read tasks from tasks.txt (JSON Lines).
    Each line is one JSON object = one task.
    Returns a list of task dictionaries.
    """
    if not os.path.exists(FILE_NAME):
        return []

    tasks: list[dict] = []
    with open(FILE_NAME, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                tasks.append(json.loads(line))
    return tasks


def save_tasks(tasks: list[dict]) -> None:
    """
    Write ALL tasks back to tasks.txt as JSON Lines.
    Rewriting the whole file keeps updates/deletes simple and consistent.
    """
    with open(FILE_NAME, "w") as f:
        for task in tasks:
            f.write(json.dumps(task) + "\n")


def find_task(task_id: int, tasks: list[dict]) -> dict:
    """
    Find a task by ID or raise a 404 error.
    Keeping this in one helper avoids repeating code.
    """
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")


# ----------------------------
# Routes / Endpoints
# ----------------------------

@app.get("/", summary="Root Check")
def root():
    """Quick health check endpoint."""
    return {
        "message": "Task Manager API is running 🚀",
        "docs": "Go to /docs for Swagger UI",
    }


# IMPORTANT: define /tasks/stats BEFORE /tasks/{task_id}
# so FastAPI doesn't treat "stats" as a task_id.
@app.get("/tasks/stats", summary="Get Task Statistics")
def task_stats():
    """
    Returns:
    - total tasks
    - completed tasks
    - pending tasks
    - completion percentage
    """
    tasks = load_tasks()
    total = len(tasks)
    completed_count = sum(1 for t in tasks if t["completed"] is True)
    pending_count = total - completed_count
    percentage = round((completed_count / total) * 100, 2) if total > 0 else 0.0

    return {
        "total": total,
        "completed": completed_count,
        "pending": pending_count,
        "completion_percentage": percentage,
    }


@app.get("/tasks", summary="Get All Tasks (optional filter)")
def get_tasks(completed: bool | None = None):
    """
    Get all tasks.
    Optional filter:
      /tasks?completed=true
      /tasks?completed=false
    """
    tasks = load_tasks()

    if completed is not None:
        tasks = [t for t in tasks if t["completed"] == completed]

    return {"tasks": tasks, "count": len(tasks)}


@app.get("/tasks/{task_id}", summary="Get One Task by ID")
def get_task(task_id: int):
    """Get a single task by ID."""
    tasks = load_tasks()
    return find_task(task_id, tasks)


@app.post("/tasks", summary="Create a Task", status_code=201)
def create_task(task_data: TaskCreate):
    """Create a new task (ID is auto-generated)."""
    tasks = load_tasks()

    # Safer than len(tasks)+1 (because deletes can create gaps)
    next_id = max((t["id"] for t in tasks), default=0) + 1

    new_task = {
        "id": next_id,
        "title": task_data.title,
        "description": task_data.description,
        "completed": False,
    }

    tasks.append(new_task)
    save_tasks(tasks)

    return new_task


@app.put("/tasks/{task_id}", summary="Update a Task")
def update_task(task_id: int, task_data: TaskUpdate):
    """
    Update any subset of fields:
    - title
    - description
    - completed
    """
    tasks = load_tasks()
    task = find_task(task_id, tasks)

    if task_data.title is not None:
        task["title"] = task_data.title
    if task_data.description is not None:
        task["description"] = task_data.description
    if task_data.completed is not None:
        task["completed"] = task_data.completed

    save_tasks(tasks)
    return task


@app.delete("/tasks/{task_id}", summary="Delete One Task by ID")
def delete_task(task_id: int):
    """Delete a task by ID."""
    tasks = load_tasks()

    # Ensure it exists (gives a clean 404 if not)
    find_task(task_id, tasks)

    updated_tasks = [t for t in tasks if t["id"] != task_id]
    save_tasks(updated_tasks)

    return {"message": f"Task {task_id} deleted"}


@app.delete("/tasks", summary="Delete All Tasks")
def delete_all_tasks():
    """Delete all tasks (clears tasks.txt)."""
    save_tasks([])
    return {"message": "All tasks deleted"}
