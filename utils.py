from datetime import datetime, timedelta, tzinfo
from typing import Optional


def sanitize_categories(category: str) -> str:
    return category.strip().lower()


class UTC(tzinfo):

    def utcoffset(self, dt: Optional[datetime]) -> Optional[timedelta]:
        return timedelta(0)

    def tzname(self, dt: Optional[datetime]) -> Optional[str]:
        return "UTC"

    def dst(self, dt: Optional[datetime]) -> Optional[timedelta]:
        return timedelta(0)