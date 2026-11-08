from pydantic import BaseModel


class TaskCreated(BaseModel):
    task_id: str
    status: str
