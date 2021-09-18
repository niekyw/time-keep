from datetime import datetime, timedelta
from typing import Optional

from pydantic import BaseModel
from fastapi import FastAPI, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()


# Can I push this?

@app.get("/")
async def root():
    return {"message": "Hello World"}


app.mount("/", StaticFiles(directory="static", html=True), name="static")
templates = Jinja2Templates(directory="templates")


class LogEntry(BaseModel):
    start_time: datetime
    end_time: datetime
    length: timedelta  # TODO: return this in some standardized unit instead?
    name: str
    category: str


NOT_FOUND_RESPONSE = {404: {"msg": str}}


@app.get("/logs/{username}", response_model=list[LogEntry])
async def get_user_logs(username: str,
                        min_time: Optional[datetime] = None,
                        max_time: Optional[datetime] = None,
                        categories: Optional[list[str]] = None) -> list[LogEntry]:
    """
    Get all the tasks from ``username`` which have been started and completed within the time
    range [``min_time``, ``max_time``]: if ``min_time`` is None, there is no lowest start time,
    and if ``max_time`` is None, there is no highest end time. All tasks must also have
    categories in ``categories``; if ``categories`` is None, tasks from all categories
    satisfying the time constraint will be provided.
    """
    raise NotImplementedError


@app.get("/categories/{username}", response_model=list[str])
async def get_user_categories(username: str) -> list[str]:
    """
    Get all the task categories constructed for / by the user ``username``.
    """
    raise NotImplementedError


# HTTP 409 is a conflict
@app.post("/categories/{username}", response_model=str)
async def add_category(username: str, category: str) -> str:
    """
    Add a new task category ``category`` for the user ``username``.
    """
    # TODO: if category already exists, raise error
    raise NotImplementedError


@app.post("/logs/start/{username}", response_model=str, status_code=status.HTTP_201_CREATED)
async def start_logging(username: str, task_name: str, category: str = "Miscellaneous") -> str:
    """
    Start logging for ``username``'s new task ``task_name`` with category ``category``.
    """
    raise NotImplementedError


@app.post("/logs/end/{username}", response_model=str, status_code=status.HTTP_201_CREATED)
async def end_logging(username: str) -> str:
    """
    End logging for ``username``'s current task.
    """
    raise NotImplementedError
