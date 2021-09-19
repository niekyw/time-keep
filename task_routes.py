import sqlite3
from datetime import datetime
from sqlite3 import Connection
from typing import Optional

from fastapi import APIRouter, Depends, status

from database_interactions import get_db
from category_routes import get_user_categories
from models import LogEntry
from utils import UTC, sanitize_categories


router = APIRouter(prefix="/tasks")


@router.get("/{username}", response_model=list[LogEntry])
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
    query = """SELECT User, Category, Start_Time, End_Time FROM tasks WHERE User = ?"""
    args = [username]
    if min_time is not None:
        min_constraint = "AND Start_Time >= ?"
        query += min_constraint
        args.append(min_time)
    if max_time is not None:
        max_constraint = "AND End_Time <= ?"
        query += max_constraint
        args.append(max_time)
    db.row_factory = sqlite3.Row
    logs = [LogEntry.from_row(row) for row in db.execute(query, args)
            if row["category"] not in categories]
    return logs


@router.post("/start/{username}", response_model=bool, status_code=status.HTTP_201_CREATED)
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
        """SELECT Task_Name FROM tasks WHERE User = ? AND End_Time IS NULL""",
        (username, )).fetchone() is not None
    if not currently_running:
        db.cursor().execute(
            """INSERT INTO tasks VALUES (?, ?, ?, ?, ?)""",
            (task_name, username, category, start_time, None)
        )
    return not currently_running


@router.post("/end/{username}", response_model=bool, status_code=status.HTTP_201_CREATED)
def end_logging(username: str, db=Depends(get_db)) -> bool:
    """
    End logging for ``username``'s current task.
    """
    db: Connection
    # Find the most recently starting event's unique identifying info
    most_recently_started = db.cursor().execute(
        """SELECT User, Task_Name, Start_Time FROM tasks WHERE User_Name = ? AND End_Time IS NULL""",
        (username, )).fetchone()
    if most_recently_started is None:
        return False
    _, task_name, start_time = most_recently_started
    utc = UTC()
    end_time = datetime.now().astimezone(utc)
    db.cursor().execute("""UPDATE tasks SET End_Time = ? WHERE User = ? AND Task_Name = ? AND Start_Time = ?""",
                        (end_time, username, task_name, start_time))
    return True