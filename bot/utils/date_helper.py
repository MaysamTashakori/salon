import jdatetime
from datetime import datetime, timedelta
import jdatetime
from datetime import datetime

def get_persian_date(date_str):
    if isinstance(date_str, str):
        date = datetime.strptime(date_str, '%Y-%m-%d')
    else:
        date = date_str
    persian_date = jdatetime.date.fromgregorian(date=date)
    return persian_date.strftime("%Y/%m/%d")

def get_available_times(service, date):
    # ساعات کاری از 9 صبح تا 9 شب
    working_hours = range(9, 21)
    duration = service.duration
    
    available_times = []
    for hour in working_hours:
        for minute in [0, 30]:
            time_str = f"{hour:02d}:{minute:02d}"
            if is_time_available(service.id, date, time_str):
                available_times.append(time_str)
    
    return available_times

def is_time_available(service_id, date, time):
    from ..database.models import Appointment
    return Appointment.check_time_availability(service_id, date, time)

def get_persian_date(gregorian_date_str):
    """Convert gregorian date string to Persian date string"""
    if isinstance(gregorian_date_str, str):
        gregorian_date = datetime.strptime(gregorian_date_str, '%Y-%m-%d')
    else:
        gregorian_date = gregorian_date_str
        
    persian_date = jdatetime.date.fromgregorian(date=gregorian_date)
    return persian_date.strftime('%Y/%m/%d')

def get_gregorian_date(persian_date_str):
    """Convert Persian date string to gregorian date string"""
    persian_date = jdatetime.datetime.strptime(persian_date_str, '%Y/%m/%d').date()
    gregorian_date = persian_date.togregorian()
    return gregorian_date.strftime('%Y-%m-%d')

def get_next_days(count=7):
    """Get next n days in Persian calendar"""
    today = jdatetime.datetime.now()
    days = []
    for i in range(count):
        next_day = today + jdatetime.timedelta(days=i)
        days.append({
            'date': next_day.strftime('%Y/%m/%d'),
            'weekday': next_day.strftime('%A')
        })
    return days