from datetime import datetime


def string_to_datetime(date_string, format_string="%Y-%m-%dT%H:%M:%S"):
    try:
        return datetime.strptime(date_string, format_string)
    except ValueError as e:
        raise ValueError(f"Error converting '{date_string}' to datetime: {e}")
