from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import os

app = FastAPI()

FILE_NAME = "tasks.txt"


class Task(BaseModel):
    id: int
    title: str
    description: str | None = None
    completed: bool = False


class TaskCreate(BaseModel):
    title: str
    description: str | None = None


def load_tasks():
    tasks = []
    if not os.path.exists(FILE_NAME):
        return tasks

    with open(FILE_NAME, "r") as f:
        for line in f:
            if line.strip():
                tasks.append(json.loads(line))
    return tasks


def save_tasks(tasks):
    with open(FILE_NAME, "w") as f:
        for task in tasks:
            f.write(json.dumps(task) + "\n")


@app.get("/")
def root():
    return {"message": "Task Manager API is running"}


@app.get("/tasks")
def get_tasks(completed: bool | None = None):
    tasks = load_tasks()

    if completed is not None:
        tasks = [t for t in tasks if t["completed"] == completed]

    return tasks


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    tasks = load_tasks()

    for task in tasks:
        if task["id"] == task_id:
            return task

    raise HTTPException(status_code=404, detail="Task not found")


@app.post("/tasks")
def create_task(task: TaskCreate):
    tasks = load_tasks()
    new_id = len(tasks) + 1

    new_task = {
        "id": new_id,
        "title": task.title,
        "description": task.description,
        "completed": False
    }

    tasks.append(new_task)
    save_tasks(tasks)

    return new_task


@app.put("/tasks/{task_id}")
def update_task(task_id: int, updated_task: TaskCreate):
    tasks = load_tasks()

    for task in tasks:
        if task["id"] == task_id:
            task["title"] = updated_task.title
            task["description"] = updated_task.description
            save_tasks(tasks)
            return task

    raise HTTPException(status_code=404, detail="Task not found")


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    tasks = load_tasks()
    new_tasks = [t for t in tasks if t["id"] != task_id]

    if len(new_tasks) == len(tasks):
        raise HTTPException(status_code=404, detail="Task not found")

    save_tasks(new_tasks)
    return {"message": "Task deleted"}


@app.delete("/tasks")
def delete_all_tasks():
    save_tasks([])
    return {"message": "All tasks deleted"}


@app.get("/tasks/stats")
def task_stats():
    tasks = load_tasks()
    total = len(tasks)
    completed = len([t for t in tasks if t["completed"]])
    pending = total - completed
    percentage = (completed / total * 100) if total > 0 else 0

    return {
        "total": total,
        "completed": completed,
        "pending": pending,
        "completion_percentage": percentage
    }
