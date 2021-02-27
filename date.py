import datetime as dt
import pytz

dt_now = dt.datetime.now(tz=pytz.UTC)
dt_newyork = dt_now.astimezone(pytz.timezone("US/Eastern"))
weekday = dt_newyork.isoweekday()
time_in_min = dt_newyork.hour * 60 + dt_newyork.minute

if weekday < 6 and time_in_min >=570 and dt_newyork.hour <16  :
    print("IsOpen")
else:
    print("is closed")