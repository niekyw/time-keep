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
        start = datetime.fromisoformat(row["Start_Time"])
        end = datetime.fromisoformat(row["End_Time"])
        return LogEntry(
            start_time=start,
            end_time=end,
            length=end - start,
            name=row["Task_Name"],
            category=row["Category"],
        )