from dateutil import parser
from datetime import datetime, timedelta, timezone
from typing import Union


def normalize_date_to_utc(date_str: str, return_type: str = None) -> Union[str, datetime]:
    date_parsed = parser.parse(date_str) + timedelta(milliseconds=100)
    date_parsed = date_parsed - timedelta(milliseconds=100)
    date_parsed = date_parsed.astimezone(timezone.utc)
    if return_type and return_type.casefold() == 'str':
        return date_parsed.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
    else:
        return date_parsed
