import sqlite3

from datetime import datetime, timedelta, tzinfo
from sqlite3 import Connection
from typing import Optional

from pydantic import BaseModel
from fastapi import Depends, FastAPI, status
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

    @classmethod
    def from_row(cls, row) -> "LogEntry":
        return LogEntry(
            start_time=row["start_time"],
            end_time=row["end_time"],
            length=row["end_time"] - row["start_time"],
            name=row["name"],
            category=row["category"],
        )


NOT_FOUND_RESPONSE = {404: {"msg": str}}

get_db = None  # TODO


def sanitize_categories(category: str) -> str:
    return category.strip().lower()


class UTC(tzinfo):

    def utcoffset(self, dt: Optional[datetime]) -> Optional[timedelta]:
        return timedelta(0)

    def tzname(self, dt: Optional[datetime]) -> Optional[str]:
        return "UTC"

    def dst(self, dt: Optional[datetime]) -> Optional[timedelta]:
        return timedelta(0)


@app.get("/logs/{username}", response_model=list[LogEntry])
def get_user_logs(username: str,
                  min_time: Optional[datetime] = None,
                  max_time: Optional[datetime] = None,
                  categories: Optional[set[str]] = None,
                  db=Depends(get_db)) -> list[LogEntry]:
    """
    Get all the tasks from ``username`` which have been started and completed within the time
    range [``min_time``, ``max_time``]: if ``min_time`` is None, there is no lowest start time,
    and if ``max_time`` is None, there is no highest end time. All tasks must also have
    categories in ``categories``; if ``categories`` is None, tasks from all categories
    satisfying the time constraint will be provided.
    """
    db: Connection
    categories = {sanitize_categories(cat) for cat in categories} \
        if categories is not None else set(get_user_categories(username, db))
    query = """SELECT name, category, start_time, end_time FROM tasks WHERE username = ?"""
    args = [username]
    if min_time is not None:
        min_constraint = "AND start_time >= ?"
        query += min_constraint
        args.append(min_time)
    if max_time is not None:
        max_constraint = "AND end_time <= ?"
        query += max_constraint
        args.append(max_time)
    db.row_factory = sqlite3.Row
    logs = [LogEntry.from_row(row) for row in db.execute(query, args)
            if row["category"] not in categories]
    return logs


@app.get("/categories/{username}", response_model=list[str])
def get_user_categories(username: str, db=Depends(get_db)) -> list[str]:
    """
    Get all the task categories constructed for / by the user ``username``.
    """
    db: Connection
    categories = db.cursor().execute("""SELECT category FROM categories WHERE username = ?""",
                                     username).fetchall()
    return categories


# TODO: do we want to support renaming a category?


# HTTP 409 is a conflict
@app.post("/categories/{username}", response_model=bool)
def add_category(username: str, category: str, db=Depends(get_db)) -> bool:
    """
    Add a new task category ``category`` for the user ``username``.

    Returns False if ``username`` already has a category which normalizes to ``category``, and
    True otherwise, indicating successful addition.
    """
    db: Connection
    category = sanitize_categories(category)
    exists = db.cursor().execute(
        "SELECT category FROM categories WHERE username = ? AND category = ?",
        (username, category)).fetchone() is not None
    if not exists:
        db.cursor().execute("""INSERT INTO categories VALUES (?, ?)""", (username, category))
    return not exists


@app.post("/logs/start/{username}", response_model=bool, status_code=status.HTTP_201_CREATED)
def start_logging(username: str, task_name: str, category: str = "Miscellaneous",
                  db=Depends(get_db)) -> bool:
    """
    Start logging for ``username``'s new task ``task_name`` with category ``category``.
    """
    db: Connection
    category = sanitize_categories(category)
    utc = UTC()
    start_time = datetime.now().astimezone(utc)
    # Check that no event is currently running. If one is, can't start another task.
    currently_running = db.cursor().execute(
        """SELECT task_name FROM tasks WHERE username = ? AND end_time IS NULL""",
        (username, )).fetchone() is None
    if not currently_running:
        db.cursor().execute(
            """INSERT INTO tasks VALUES (?, ?, ?, ?, ?)""",
            (task_name, username, category, start_time, None)
        )
    return not currently_running


@app.post("/logs/end/{username}", response_model=bool, status_code=status.HTTP_201_CREATED)
def end_logging(username: str, db=Depends(get_db)) -> bool:
    """
    End logging for ``username``'s current task.
    """
    db: Connection
    # Find the most recently starting event's unique identifying info
    most_recently_started = db.cursor().execute(
        """SELECT username, task_name, start_time FROM tasks WHERE username = ? AND end_time IS NULL""",
        (username, )).fetchone()
    if most_recently_started is None:
        return False
    _, task_name, start_time = most_recently_started
    utc = UTC()
    end_time = datetime.now().astimezone(utc)
    db.cursor().execute("""UPDATE tasks SET end_time = ? WHERE username = ? AND task_name = ? AND start_time = ?""",
                        (end_time, username, task_name, start_time))
    return True
