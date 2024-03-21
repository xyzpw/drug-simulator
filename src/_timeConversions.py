import datetime
import re
import time

readableTimePattern = re.compile(r"^(?P<hour>\d{1,2}):(?P<minute>\d{1,2})$")
timePattern = re.compile(r"^(?P<time>\d+|\d+\.\d+|\.\d+)(?:(?:\s)?(?P<unit>s|sec|second(?:s)?|m|min|minute(?:s)?|h|hour(?:s)?|d|day(?:s)?))?$")
def getHoursAndMinutesFromReadableTime(readableTime) -> tuple:
    readableTimePatternSearch = readableTimePattern.search(readableTime)
    if bool(readableTimePatternSearch):
        hour = readableTimePatternSearch.group("hour")
        minute = readableTimePatternSearch.group("minute")
        hour, minute = int(hour), int(minute)
        if hour > 24 or minute > 60 or (hour == 24 and minute > 59):
            raise ValueError("time must be less than 24 hours")
        return hour, minute
    raise ValueError("time format must be 24-hour format")

def getEpochFromHourAndMinute(hour, minute) -> float:
    day = datetime.datetime.now().day
    month = datetime.datetime.now().month
    year = datetime.datetime.now().year
    epochAtReadableTime = datetime.datetime(year, month, day, hour, minute).timestamp()
    return epochAtReadableTime

def getSecondsFromHourAndMinute(hour, minute) -> float:
    hours = hour + (minute / 60)
    return (hours) * 3600

def getEpochFromElapseTime(hour, minute) -> int:
    seconds = getSecondsFromHourAndMinute(hour, minute)
    return int(time.time()) - int(seconds)

def convertToSeconds(_time, unit) -> float:
    if unit == None:
        return _time
    unit = unit[0]
    match unit:
        case "h":
            return _time * 3600
        case "m":
            return _time * 60
        case "d":
            return _time * 86400
    return _time

def fixTimeUI(timeUI: str) -> float:
    if timeUI in ['', None]:
        return
    if not isinstance(timeUI, str):
        timeUI = str(timeUI)
    timePatternSearch = timePattern.search(timeUI)
    try:
        unfixedTime = float(timePatternSearch.group("time"))
    except:
        raise ValueError(f"invalid time input: '{timeUI}'")
    if bool(timePatternSearch.group("unit")):
        unit = timePatternSearch.group("unit")
        fixedTime = convertToSeconds(unfixedTime, unit)
        return float(fixedTime)
    else:
        return float(unfixedTime)
