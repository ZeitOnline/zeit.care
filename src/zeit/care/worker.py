import datetime
import pytz

def isofy_date_last_modified(date):
    dt = datetime.datetime.strptime(date, "%d.%m.%Y - %H:%M")
    dt = dt.replace(tzinfo=pytz.timezone("Europe/Berlin")).astimezone(pytz.UTC)
    return dt.isoformat()
