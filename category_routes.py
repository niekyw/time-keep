from sqlite3 import Connection

from fastapi import Depends, APIRouter, status

from database_interactions import get_db
from utils import sanitize_categories

router = APIRouter(prefix="/categories")


@router.get("/{username}", response_model=list[str])
def get_user_categories(username: str, db=Depends(get_db)) -> list[str]:
    """
    Get all the task categories constructed for / by the user ``username``.
    """
    db: Connection
    categories = db.cursor().execute("""SELECT Category FROM categories WHERE User = ?""",
                                     (username, )).fetchall()
    return [category for category, *_ in categories]


# HTTP 409 is a conflict
@router.post("/{username}", response_model=bool, status_code=status.HTTP_201_CREATED)
def add_category(username: str, category: str, db=Depends(get_db)) -> bool:
    """
    Add a new task category ``category`` for the user ``username``.

    Returns False if ``username`` already has a category which normalizes to ``category``, and
    True otherwise, indicating successful addition.
    """
    db: Connection
    category = sanitize_categories(category)
    exists = db.cursor().execute(
        "SELECT Category FROM categories WHERE User = ? AND Category = ?",
        (username, category)).fetchone() is not None
    if not exists:
        db.cursor().execute("""INSERT INTO categories (User, Category) VALUES (?, ?)""",
                            (username, category))
        db.commit()

    return not exists
