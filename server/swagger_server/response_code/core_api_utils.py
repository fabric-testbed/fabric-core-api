import uuid
from datetime import datetime, timedelta, timezone
from typing import Union

from dateutil import parser


def normalize_date_to_utc(date_str: str, return_type: str = None) -> Union[None, str, datetime]:
    try:
        date_parsed = parser.parse(date_str) + timedelta(milliseconds=100)
        date_parsed = date_parsed - timedelta(milliseconds=100)
        date_parsed = date_parsed.astimezone(timezone.utc)
    except Exception as exc:
        print(exc)
        return None
    if return_type and return_type.casefold() == 'str':
        return date_parsed.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
    else:
        return date_parsed


def is_valid_uuid(val) -> bool:
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False
