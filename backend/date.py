from datetime import datetime, timedelta

WEEKDAY_MAP = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6
}

def date_to_weekday(date_str):
    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    return date_obj.strftime("%A")

def weekday_to_date(weekday, reference_date=None, force_future=False):
    if reference_date is None:
        reference_date = datetime.now().date()

    target = WEEKDAY_MAP[weekday]

    days_ahead = (target - reference_date.weekday()) % 7

    if force_future and days_ahead == 0:
        days_ahead = 7

    return reference_date + timedelta(days=days_ahead)