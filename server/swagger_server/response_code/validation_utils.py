from datetime import datetime

_datetime_formats = ['%A, %B %d, %Y', '%A, %B %d, %Y %I:%M:%S %p %Z', '%A, %d %B %Y', '%B %d %Y', '%B %d, %Y',
                     '%H:%M:%S', '%H:%M:%S,%f', '%H:%M:%S.%f', '%Y %b %d %H:%M:%S.%f', '%Y %b %d %H:%M:%S.%f %Z',
                     '%Y %b %d %H:%M:%S.%f*%Z', '%Y%m%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S %z', '%Y-%m-%d %H:%M:%S%z',
                     '%Y-%m-%d %H:%M:%S,%f', '%Y-%m-%d %H:%M:%S,%f%z', '%Y-%m-%d %H:%M:%S.%f',
                     '%Y-%m-%d %H:%M:%S.%f%z', '%Y-%m-%d %I:%M %p', '%Y-%m-%d %I:%M:%S %p', '%Y-%m-%d*%H:%M:%S',
                     '%Y-%m-%d*%H:%M:%S:%f', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S%Z', '%Y-%m-%dT%H:%M:%S%z',
                     '%Y-%m-%dT%H:%M:%S*%f%z', '%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S.%f%z', '%Y/%m/%d',
                     '%Y/%m/%d*%H:%M:%S', '%a %b %d %H:%M:%S %Z %Y', '%a, %d %b %Y %H:%M:%S %z', '%b %d %H:%M:%S',
                     '%b %d %H:%M:%S %Y', '%b %d %H:%M:%S %z', '%b %d %H:%M:%S %z %Y', '%b %d %Y', '%b %d %Y %H:%M:%S',
                     '%b %d, %Y', '%b %d, %Y %I:%M:%S %p', '%b.%d.%Y', '%d %B %Y', '%d %B %Y %H:%M:%S %Z',
                     '%d %b %Y %H:%M:%S', '%d %b %Y %H:%M:%S %z', '%d %b %Y %H:%M:%S*%f', '%d%m_%H:%M:%S',
                     '%d%m_%H:%M:%S.%f', '%d-%b-%Y', '%d-%b-%Y %H:%M:%S', '%d-%b-%Y %H:%M:%S.%f',
                     '%d-%b-%Y %I:%M:%S %p', '%d-%m-%Y', '%d-%m-%Y %I:%M %p', '%d-%m-%Y %I:%M:%S %p',
                     '%d-%m-%y', '%d-%m-%y %I:%M %p', '%d-%m-%y %I:%M:%S %p', '%d/%b %H:%M:%S,%f', '%d/%b/%Y %H:%M:%S',
                     '%d/%b/%Y %I:%M %p', '%d/%b/%Y:%H:%M:%S', '%d/%b/%Y:%H:%M:%S %z', '%d/%m/%Y',
                     '%d/%m/%Y %H:%M:%S %z', '%d/%m/%Y %I:%M %p', '%d/%m/%Y %I:%M:%S %p', '%d/%m/%Y %I:%M:%S %p:%f',
                     '%d/%m/%Y*%H:%M:%S', '%d/%m/%Y*%H:%M:%S*%f', '%d/%m/%y', '%d/%m/%y %H:%M:%S',
                     '%d/%m/%y %H:%M:%S %z', '%d/%m/%y %I:%M %p', '%d/%m/%y %I:%M:%S %p', '%d/%m/%y*%H:%M:%S',
                     '%m%d_%H:%M:%S', '%m%d_%H:%M:%S.%f', '%m-%d-%Y', '%m-%d-%Y %I:%M %p', '%m-%d-%Y %I:%M:%S %p',
                     '%m-%d-%y', '%m-%d-%y %I:%M %p', '%m-%d-%y %I:%M:%S %p', '%m/%d/%Y', '%m/%d/%Y %H:%M:%S %z',
                     '%m/%d/%Y %I:%M %p', '%m/%d/%Y %I:%M:%S %p', '%m/%d/%Y %I:%M:%S %p:%f', '%m/%d/%Y*%H:%M:%S',
                     '%m/%d/%Y*%H:%M:%S*%f', '%m/%d/%y', '%m/%d/%y %H:%M:%S', '%m/%d/%y %H:%M:%S %z',
                     '%m/%d/%y %I:%M %p', '%m/%d/%y %I:%M:%S %p', '%m/%d/%y*%H:%M:%S', '%y%m%d %H:%M:%S',
                     '%y-%m-%d %H:%M:%S', '%y-%m-%d %H:%M:%S,%f', '%y-%m-%d %H:%M:%S,%f %z', '%y/%m/%d %H:%M:%S']


def parse_timestamp(datetime_string: str) -> bool:
    for f in _datetime_formats:
        try:
            datetime.strptime(datetime_string, f)
            return True
        except Exception:
            continue
    return False
