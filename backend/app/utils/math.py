import datetime


def float_range(values, start_key, end_key):
    start = 0
    if values[start_key]:
        start = float(values[start_key])

    end = 0
    if values[end_key]:
        end = float(values[end_key])

    return start, end


def int_range(values, start_key, end_key):
    start = 0
    if values[start_key]:
        start = int(values[start_key])

    end = 0
    if values[end_key]:
        end = int(values[end_key])

    return start, end


def format_delta_time(delta_time: datetime.timedelta) -> str:
    """
    Format a timedelta object into a string.

    :param delta_time: The timedelta object to format.
    :return: A string that represents the time difference in weeks, days, hours, and minutes.
    """

    delta_time_seconds = delta_time.days * 24 * 3600 + delta_time.seconds
    delta_time_minutes, delta_time_seconds = divmod(delta_time_seconds, 60)
    delta_time_hours, delta_time_minutes = divmod(delta_time_minutes, 60)
    delta_time_days, delta_time_hours = divmod(delta_time_hours, 24)
    delta_time_weeks, delta_time_days = divmod(delta_time_days, 7)

    delta_time_formatted = ""
    add_space = False

    if delta_time_weeks > 0:
        delta_time_formatted += f"{delta_time_weeks}w"
        add_space = True

    if delta_time_days > 0:
        delta_time_formatted += f"{' ' if add_space else ''}{delta_time_days}d"
        add_space = True

    if delta_time_hours > 0:
        delta_time_formatted += f"{' ' if add_space else ''}{delta_time_hours}h"
        add_space = True

    if delta_time_minutes > 0:
        delta_time_formatted += f"{' ' if add_space else ''}{delta_time_minutes}m"

    return delta_time_formatted
