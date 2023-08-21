import datetime as dt

import calendar
import pytz


TZ_PARIS = 'Europe/Paris'
TZ_ZURICH = 'Europe/Zurich'


def localise_date_interval(date_start, date_end, timezone_name=TZ_PARIS):
    return (localise_date(date_start, timezone_name=timezone_name),
            localise_date(date_end, time=dt.time.max, timezone_name=timezone_name))


def localise_date(pydate, time=dt.time(), timezone_name=TZ_PARIS):
    return pytz.timezone(timezone_name).localize(dt.datetime.combine(pydate, time))


def localise_datetime(pydatetime, timezone_name=TZ_PARIS):
    return pytz.timezone(timezone_name).localize(pydatetime)


def localised_year_interval(year: [int, list], timezone_name=TZ_PARIS):
    if isinstance(year, list):
        return localise_date_interval(dt.date(min(year), 1, 1), dt.date(max(year), 12, 31), timezone_name=timezone_name)
    else:
        return localise_date_interval(dt.date(year, 1, 1), dt.date(year, 12, 31), timezone_name=timezone_name)


def localised_month_interval(year: int, month: int, timezone_name=TZ_PARIS):
    start_date = dt.date(year, month, 1)
    end_date = dt.date(year, month, calendar.monthrange(year, month)[1])
    return localise_date_interval(start_date, end_date, timezone_name)


def convert_timezone(pydatetime, timezone_name=TZ_PARIS):
    return pydatetime.astimezone(pytz.timezone(timezone_name))