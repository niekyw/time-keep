from datetime import datetime, timedelta

from pydantic import BaseModel


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