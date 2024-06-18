import datetime
import re
import time

timePattern = re.compile(r"^(?P<time>\d+|\d+\.\d+|\.\d+)(?:(?:\s)?(?P<unit>s|sec|second(?:s)?|m|min|minute(?:s)?|h|hour(?:s)?|d|day(?:s)?))?$")

readableTimePattern = re.compile(r"\A(?P<time>\d{1,2}:\d{1,2}|\d{4})\Z")
datetimePattern = re.compile(r"^(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})\s?(?P<hour>\d{2})(?P<minute>\d{2})$")
def getHoursAndMinutesFromReadableTime(readableTime) -> tuple:
    try:
        hoursAndMinutes = readableTimePattern.search(readableTime).group("time")
        if ":" in hoursAndMinutes:
            hours, minutes = re.search(r"(\d{1,2}):(\d{1,2})", hoursAndMinutes).groups()
        else:
            hours, minutes = re.search(r"\A(?P<h>\d{2})(?P<m>\d{2})\Z", hoursAndMinutes).groups()
        hours, minutes = int(hours), int(minutes)
        if 24 < hours < 0 or 24 < minutes < 0:
            raise SystemExit("time must be less than 24 hours")
        return hours, minutes
    except:
        raise SystemExit("time format must be 24-hour format")

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

def fixTimeUI(timeUi: str) -> float:
    if timeUi in ['', None]:
        return
    if not isinstance(timeUi, str):
        timeUi = str(timeUi)
    if "/" in timeUi:
        from src._uiHandler import getValueFromFraction
        timeUiFractionValue = getValueFromFraction(timeUi)
        timeUi = re.sub(r"^((?:\d*\.)?\d+/(?:\d*\.)?\d+)", f"{timeUiFractionValue}", timeUi)
    timePatternSearch = timePattern.search(timeUi)
    try:
        unfixedTime = float(timePatternSearch.group("time"))
    except:
        raise ValueError(f"invalid time input: '{timeUi}'")
    if bool(timePatternSearch.group("unit")):
        unit = timePatternSearch.group("unit")
        fixedTime = convertToSeconds(unfixedTime, unit)
        return float(fixedTime)
    else:
        return float(unfixedTime)

def getEpochFromDatetime(usrDatetime: str) -> float:
    dateRegexMatch = datetimePattern.search(usrDatetime)
    dateReGroup = lambda g: int(dateRegexMatch.group(g))
    epoch = datetime.datetime(
        dateReGroup("year"),
        dateReGroup("month"),
        dateReGroup("day"),
        dateReGroup("hour"),
        dateReGroup("minute")
    ).timestamp()
    return epoch
