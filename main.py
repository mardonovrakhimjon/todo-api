import uvicorn
from fastapi import FastAPI, Query, Body, Path
from sqlalchemy.orm import Session
from models import engine, Tasks, Base

app = FastAPI()
Base.metadata.create_all(engine)


@app.get("/health")
def health_view() -> dict:
    return {"message": "ok"}


@app.get("/api/tasks")
def get_tasks_view(
    limit: int = Query(10),
    title: str = Query(''),
) -> list[dict]:
    with Session(engine) as session:
        tasks: list[Tasks] = session.query(Tasks).all()
        
    result = []
    for task in tasks:
        result.append({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
        })
        
    if title:
        return [task for task in result if title.lower() in task['title'].lower()][:limit]
    return result[:limit]


@app.get("/api/tasks/{task_id}")
def get_task_detail_view(task_id: int) -> dict:
    with Session(engine) as session:
        task: Tasks | None = session.query(Tasks).get(task_id)
        
    if task:
        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
        }
    return {'message': 'not found'}
        
    

@app.post("/api/tasks")
def create_task_view(
    data: dict = Body()
) -> dict:
    task = Tasks(**data)
    with Session(engine) as session:
        session.add(task)
        session.commit()
        session.refresh(task)

    return {'message': 'ok'}


@app.put("/api/tasks/{task_id}")
def update_task_view(
    task_id: int = Path(),
    data: dict = Body()
) -> dict:
    with Session(engine) as session:
        task = session.query(Tasks).get(task_id)
        if not task:
            return {'message': 'task not found'}
        for key, value in data.items():
            setattr(task, key, value)
        session.commit()
        session.refresh(task)
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
    }


@app.patch("/api/tasks/{task_id}/completed")
def mark_as_completed_view(
    task_id: int = Path()
) -> dict:
    with Session(engine) as session:
        task = session.query(Tasks).get(task_id)
        if not task:
            return {'message': 'task not found'}
        task.status = 'completed'
        session.commit()
        session.refresh(task)
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
    }


@app.patch("/api/tasks/{task_id}/incompleted")
def mark_as_incompleted_view(
    task_id: int = Path()
) -> dict:
    with Session(engine) as session:
        task = session.query(Tasks).get(task_id)
        if not task:
            return {'message': 'task not found'}
        task.status = 'incompleted'
        session.commit()
        session.refresh(task)
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
    }


@app.delete("/api/tasks/{task_id}")
def delete_task_view(
    task_id: int = Path()
) -> dict:
        with Session(engine) as session:
            task = session.query(Tasks).get(task_id)
            if not task:
                return {'message': 'task not found'}
            session.delete(task)
            session.commit()
        return {'message': 'task deleted'}


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8080, reload=True)
