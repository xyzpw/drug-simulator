#!/usr/bin/env python3

import time
import datetime
import argparse
import re
import math

parser = argparse.ArgumentParser(
    description="description: Simulates the absorption and elimination of drugs.",
    add_help=False,
)
parser.add_argument("--help", "-h", help="displays help and exits", action="help")
parser.add_argument("--units", help="displays available time units [default: seconds]", action="store_true")
parser.add_argument("--dose", help="the dosage to be simulated", metavar="<dose>")
parser.add_argument("--tmax", help="time it takes to reach peak concentration", metavar="<time>[ unit]")
parser.add_argument("--t12a", help="absorption half-life of the drug to be simulated", metavar="<time>[ unit]")
parser.add_argument("--t12", help="half-life of the drug to be simulated", metavar="<time>[ unit]")
parser.add_argument("--probability", help="display concentration as probability of drug remaining", action="store_true")
parser.add_argument("--linear", help="calculates and uses elimination constant of given half-life", action="store_true")
parser.add_argument("--lineara", help="uses linear absorption regardless of method", action="store_true")
parser.add_argument("--time", help="time the dose was administered in 24-hour format", metavar="HH:MM")
parser.add_argument("--elapse", help="how much time has passed since the simulation was started", metavar="HH:MM")
parser.add_argument("--tmaxed", help="starts simulation assuming the drug has already peaked", action="store_true")
parser.add_argument("-p", help="decimal places to keep for displayed results", metavar="decimal_precision", dest="precision", default=0)
parser.add_argument("-f", help="bioavailability of the drug being simulated", metavar="decimal", dest="bioavailability")
parser.add_argument("--autocomplete", help="immediatly exits once concentration reaches 0", action="store_true")
parser.add_argument("--dr", help="duration until second part of dose is released (delayed release form)", metavar="<time>[ unit]")
parser.add_argument("--irfrac", help="fraction of dose that is instant release (used with dr)", metavar="<time>[ unit]")
parser.add_argument("--lagtime", help="time taken for drug to appear", metavar="<time>[ unit]")
parser.add_argument("--msg", help="custom message on start", metavar="msg")
args = vars(parser.parse_args())

if args.get("irfrac") != None and args.get("dr") == None:
    raise SystemExit("irfrac can only be used with delayed release")
if args.get("irfrac") != None:
    if float(args.get("irfrac")) >= 1 or float(args.get("irfrac")) <= 0:
        raise SystemExit("irfrac must be greater than 0 and less than 1")

if args.get("units"):
    print("available units: (s)econds, (m)inutes, (h)ours, (d)ays")
    raise SystemExit(0)

useProbability, useLinear, startAtCmax = args.get("probability"), args.get("linear"), args.get("tmaxed")
if startAtCmax and args.get("lagtime") != None:
    raise SystemExit("tmaxed and lagtime cannot be active simultaneously")
precision = args.get("precision")
if precision != None:
    try:
        precision = int(precision)
    except:
        raise SystemExit("precision must be an integer")
    if precision not in range(0, 15+1):
        raise SystemExit("precision must be from 0 to 15")

if useProbability and useLinear:
    raise SystemExit("probability and linear cannot be active simultaneously")
if args.get("time") and args.get("elapse"):
    raise SystemExit("time and elapse cannot be used simultaneously")


readableTimePattern = re.compile(r"^(?P<hour>\d{1,2}):(?P<minute>\d{1,2})$")
timePattern = re.compile(r"^(?P<time>\d+|\d+\.\d+|\.\d+)(?:(?:\s)?(?P<unit>s|sec|second(?:s)?|m|min|minute(?:s)?|h|hour(?:s)?|d|day(?:s)?))?$")
def getEpoch(asInt=True) -> float | int:
    if asInt:
        return time.time() // 1
    return time.time()
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
    return getEpoch() - int(seconds)

def getUIValue(uiTxt, argLocation=None, inputText=None):
    if argLocation == None:
        argLocation = uiTxt
    if inputText == None:
        inputText = uiTxt
    if args.get(argLocation) == None:
        return input(f"{inputText}: ")
    else:
        return args.get(argLocation)

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

def fixTimeUI(timeUI) -> float:
    if timeUI in ['', None]:
        return None
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

# user input
try:
    if not useProbability:
        dose = getUIValue("dose", inputText="dose")
    else:
        dose = float(1)
    if not startAtCmax:
        tmax = getUIValue("tmax", inputText="tmax")
        tmax = fixTimeUI(tmax)
    else:
        tmax = float(0)
    if not startAtCmax and not args.get("lineara"):
        t12a = getUIValue("t12a", inputText="absorption half-life")
        t12a = fixTimeUI(t12a)
    t12 = getUIValue("t12", inputText="half-life")
    t12 = fixTimeUI(t12)
    if args.get("bioavailability") != None and not useProbability:
        try:
            _bioavailability = float(args.get("bioavailability"))
            if _bioavailability >= 1 or _bioavailability <= 0:
                raise SystemExit("bioavailability must be greater than 0 or less than 1")
            dose = float(args.get("bioavailability")) * float(dose)
        except:
            raise ValueError("bioavailability must be decimal value")
    if args.get("dr") != None:
        DrLagTime = fixTimeUI(args.get("dr"))
        # Instant release fraction is released instantly, the remaining dose is released after a given time.
        IRFrac = fixTimeUI(getUIValue("irfrac", inputText="instant release dose fraction (def. 0.5)"))
        if IRFrac in [None, '']: IRFrac = 0.5
        if 1 < IRFrac <= 0:
            raise SystemExit("instant release must be between 0 to 1")
except (KeyboardInterrupt, EOFError):
    print("\n", end='')
    raise SystemExit(0)
except Exception as ERROR:
    print("\n", end='')
    raise SystemExit(ERROR)

def getMethod():
    if useProbability:
        return "probability"
    elif useLinear:
        return "linear"
    return "default"

def getStartingTime() -> float:
    if args.get("time"):
        try:
            hour, minute = getHoursAndMinutesFromReadableTime(str(args.get("time")))
            return getEpochFromHourAndMinute(hour, minute)
        except:
            raise ValueError("invalid time value")
    elif args.get("elapse") != None:
        try:
            hour, minute = getHoursAndMinutesFromReadableTime(str(args.get("elapse")))
            return getEpochFromElapseTime(hour, minute)
        except:
            raise ValueError("invalid elapse value")
    return getEpoch()

def getConstant(halflife) -> float:
    return math.log(2) / halflife

def getConcentration(dosage, halflife, timeElapsed, tmaxed=False) -> float:
    halflife = float(halflife)
    dosage = float(dosage)
    timeElapsed = float(timeElapsed)
    match method:
        case "default":
            halfLivesPassed = timeElapsed / halflife
            if tmaxed:
                return dosage * 0.5**halfLivesPassed
            else:
                return dosage - (dosage * 0.5**halfLivesPassed)
        case "linear":
            ke = getConstant(halflife)
            fracDose = 1 - (ke * timeElapsed)
            halfLivesPassed = timeElapsed / halflife
            if tmaxed:
                return dosage * fracDose
            else:
                return dosage - (dosage * 0.5**halfLivesPassed)
                # return dosage * (timeElapsed / tmax)
        case "probability":
            halfLivesPassed = timeElapsed / halflife
            if tmaxed:
                return 0.5**halfLivesPassed
            else:
                return 1 - 0.5**halfLivesPassed

def completeScript():
    if args.get("autocomplete"):
        raise SystemExit(0)
    print('\n', end='')
    input("Finished. Press enter to exit")
    raise SystemExit(0)

def checkIfEliminated(concentration, phase=None):
    if concentration <= 0 and phase in ["elimination", None]:
        completeScript()

def fixForPrecision(val) -> float | int:
    if precision == 0:
        return int(val)
    if not isinstance(val, float):
        raise TypeError("fix for precision value must be a float".format(val))
    val = math.floor(val * 10**precision) / 10**precision
    return val

usingTimeOrElapse = args.get("time") != None or args.get("elapse") != None
updateIntervalSeconds = 1/20
isDR = args.get("dr")

def startDefault():
    currentConcentration = dose if startAtCmax else 0
    hasTmaxed = True if startAtCmax else False
    # skip distribution
    phase = "absorption" if not hasTmaxed else "elimination"
    timeSinceTmax = None
    tmaxedEpoch = None
    if args.get("lagtime") != None and usingTimeOrElapse:
        startingEpoch = getStartingTime() + fixTimeUI(getUIValue("lagtime"))
    else:
        startingEpoch = getStartingTime()
    if usingTimeOrElapse:
        tmaxedEpoch = startingEpoch + tmax
    elif startAtCmax:
        tmaxedEpoch = startingEpoch
    while True:
        time.sleep(updateIntervalSeconds)
        timeSinceStart = getEpoch(False) - startingEpoch
        if hasTmaxed == False:
            hasTmaxed = True if timeSinceStart >= tmax else False
            if hasTmaxed:
                phase = "elimination"
                if not usingTimeOrElapse:
                    tmaxedEpoch = getEpoch(False)
                currentConcentration = dose
        if hasTmaxed:
            timeSinceTmax = getEpoch(False) - tmaxedEpoch
            currentConcentration = getConcentration(dose, t12, timeSinceTmax, tmaxed=True)
            currentConcentration = fixForPrecision(currentConcentration)
        else:
            if args.get("lineara"):
                currentConcentration = float(dose) * (timeSinceStart / tmax)
            else:
                currentConcentration = getConcentration(dose, t12a, timeSinceStart, tmaxed=False)
            currentConcentration = fixForPrecision(currentConcentration)
        print(f"\033[2Kconcentration ({phase}): {currentConcentration}", end='\r', flush=True)
        checkIfEliminated(currentConcentration, phase)

def startDefaultDR():
    currentConcentration = float(dose)*IRFrac if startAtCmax else 0
    hasTmaxed = True if startAtCmax else False
    phase = "absorption" if not hasTmaxed else "elimination"
    timeSinceTmax = None
    tmaxedEpoch = None
    delayedTmaxEpoch = None
    delayedReleaseStarted = False
    timeSinceDelayedTmax = 0
    if args.get("lagtime") != None and usingTimeOrElapse:
        startingEpoch = getStartingTime() + fixTimeUI(getUIValue("lagtime"))
    else:
        startingEpoch = getStartingTime()
    currentDelayedConcentration = 0
    delayedStartingEpoch = startingEpoch + fixTimeUI(getUIValue("dr"))
    if startingEpoch < (DrLagTime + startingEpoch):
        delayedPhase = "lag"
        delayedHasTmaxed = False
    elif startingEpoch < (DrLagTime + startingEpoch + tmax):
        delayedPhase = "absorption"
        delayedHasTmaxed = False
        delayedReleaseStarted = True
    elif startingEpoch >= (DrLagTime + startingEpoch + tmax):
        delayedPhase = "elimination"
        delayedHasTmaxed = True
    if usingTimeOrElapse:
        tmaxedEpoch = startingEpoch + tmax
        delayedTmaxEpoch = delayedStartingEpoch + tmax
    elif startAtCmax:
        tmaxedEpoch = startingEpoch
    while True:
        time.sleep(updateIntervalSeconds)
        timeSinceStart = getEpoch(False) - startingEpoch
        timeSinceDelayedStart = getEpoch(False) - delayedStartingEpoch
        if not delayedReleaseStarted:
            delayedReleaseStarted = True if timeSinceStart >= DrLagTime else False
            delayedPhase = "absorption" if delayedReleaseStarted else "lag"
        if not hasTmaxed:
            hasTmaxed = True if timeSinceStart >= tmax else False
            if hasTmaxed:
                phase = "elimination"
                if not usingTimeOrElapse:
                    tmaxedEpoch = getEpoch(False)
                currentConcentration = float(dose)*IRFrac
        if hasTmaxed:
            timeSinceTmax = getEpoch(False) - tmaxedEpoch
            currentConcentration = getConcentration(float(dose)*IRFrac, t12, timeSinceTmax, tmaxed=True)
        else:
            if args.get("lineara"):
                currentConcentration = float(dose)*IRFrac * (timeSinceStart / tmax)
            else:
                currentConcentration = getConcentration(float(dose)*IRFrac, t12a, timeSinceStart, tmaxed=False)
        if not delayedHasTmaxed:
            delayedHasTmaxed = True if timeSinceStart >= (DrLagTime + tmax) else False
            if delayedHasTmaxed:
                delayedPhase = "elimination"
                if not usingTimeOrElapse:
                    delayedTmaxEpoch = getEpoch(False)
                currentDelayedConcentration = float(dose)*(1-IRFrac)
        if delayedReleaseStarted:
            if delayedHasTmaxed:
                timeSinceDelayedTmax = getEpoch(False) - delayedTmaxEpoch
                currentDelayedConcentration = getConcentration(float(dose)*(1-IRFrac), t12, timeSinceDelayedTmax, tmaxed=True)
            else:
                if args.get("lineara"):
                    currentDelayedConcentration = float(dose)*(1-IRFrac) * (timeSinceDelayedStart / tmax)
                else:
                    currentDelayedConcentration = getConcentration(float(dose)*(1-IRFrac), t12a, timeSinceDelayedStart, tmaxed=False)
        totalConcentration = currentConcentration + currentDelayedConcentration
        totalConcentration = fixForPrecision(totalConcentration)
        print(f"\033[2Kconcentration ({phase}[DR: {delayedPhase}]): {totalConcentration}", end='\r', flush=True)
        checkIfEliminated(totalConcentration, delayedPhase)

def startLinear():
    currentConcentration = dose if startAtCmax else 0
    hasTmaxed = True if startAtCmax else False
    phase = "absorption" if not hasTmaxed else "elimination"
    timeSinceTmax = None
    tmaxedEpoch = None
    if args.get("lagtime") != None and usingTimeOrElapse:
        startingEpoch = getStartingTime() + fixTimeUI(getUIValue("lagtime"))
    else:
        startingEpoch = getStartingTime()
    if usingTimeOrElapse:
        tmaxedEpoch = startingEpoch + tmax
    elif startAtCmax:
        tmaxedEpoch = startingEpoch
    while True:
        time.sleep(updateIntervalSeconds)
        timeSinceStart = getEpoch(False) - startingEpoch
        if hasTmaxed == False:
            hasTmaxed = True if timeSinceStart >= tmax else False
            if hasTmaxed:
                phase = "elimination"
                if not usingTimeOrElapse:
                    tmaxedEpoch = getEpoch(False)
                currentConcentration = dose
        if hasTmaxed:
            timeSinceTmax = getEpoch(False) - tmaxedEpoch
            currentConcentration = getConcentration(dose, t12, timeSinceTmax, tmaxed=True)
            currentConcentration = fixForPrecision(currentConcentration)
        else:
            if args.get("lineara"):
                currentConcentration = float(dose) * (timeSinceStart / tmax)
            else:
                currentConcentration = getConcentration(dose, t12a, timeSinceStart, tmaxed=False)
            currentConcentration = fixForPrecision(currentConcentration)
        print(f"\033[2Kconcentration ({phase}): {currentConcentration}", end='\r', flush=True)
        checkIfEliminated(currentConcentration, phase)

def startLinearDR():
    currentConcentration = float(dose)*IRFrac if startAtCmax else 0
    hasTmaxed = True if startAtCmax else False
    phase = "absorption" if not hasTmaxed else "elimination"
    timeSinceTmax = None
    tmaxedEpoch = None
    delayedTmaxEpoch = None
    delayedReleaseStarted = False
    timeSinceDelayedTmax = 0
    if args.get("lagtime") != None and usingTimeOrElapse:
        startingEpoch = getStartingTime() + fixTimeUI(getUIValue("lagtime"))
    else:
        startingEpoch = getStartingTime()
    currentDelayedConcentration = 0
    delayedStartingEpoch = startingEpoch + fixTimeUI(getUIValue("dr"))
    if startingEpoch < (DrLagTime + startingEpoch):
        delayedPhase = "lag"
        delayedHasTmaxed = False
    elif startingEpoch < (DrLagTime + startingEpoch + tmax):
        delayedPhase = "absorption"
        delayedHasTmaxed = False
    elif startingEpoch >= (DrLagTime + startingEpoch + tmax):
        delayedPhase = "elimination"
        delayedHasTmaxed = True
    if usingTimeOrElapse:
        tmaxedEpoch = startingEpoch + tmax
        delayedTmaxEpoch = delayedStartingEpoch + tmax
    elif startAtCmax:
        tmaxedEpoch = startingEpoch
    while True:
        time.sleep(updateIntervalSeconds)
        timeSinceStart = getEpoch(False) - startingEpoch
        timeSinceDelayedStart = getEpoch(False) - delayedStartingEpoch
        if not delayedReleaseStarted:
            delayedReleaseStarted = True if timeSinceStart >= DrLagTime else False
            delayedPhase = "absorption" if delayedReleaseStarted else "lag"
        if not hasTmaxed:
            hasTmaxed = True if timeSinceStart >= tmax else False
            if hasTmaxed:
                phase = "elimination"
                if not usingTimeOrElapse:
                    tmaxedEpoch = getEpoch(False)
                currentConcentration = float(dose)*IRFrac
        if hasTmaxed:
            timeSinceTmax = getEpoch(False) - tmaxedEpoch
            currentConcentration = getConcentration(float(dose)*IRFrac, t12, timeSinceTmax, tmaxed=True)
        else:
            if args.get("lineara"):
                currentConcentration = float(dose)*IRFrac / (timeSinceStart / tmax)
            else:
                currentConcentration = getConcentration(float(dose)*IRFrac, t12, timeSinceStart, tmaxed=False)
        if not delayedHasTmaxed:
            delayedHasTmaxed = True if timeSinceStart >= (DrLagTime + tmax) else False
            if delayedHasTmaxed:
                delayedPhase = "elimination"
                if not usingTimeOrElapse:
                    delayedTmaxEpoch = getEpoch(False)
                currentDelayedConcentration = float(dose)*(1-IRFrac)
        if delayedReleaseStarted:
            if delayedHasTmaxed:
                timeSinceDelayedTmax = getEpoch(False) - delayedTmaxEpoch
                currentDelayedConcentration = getConcentration(float(dose)*(1-IRFrac), t12, timeSinceDelayedTmax, tmaxed=True)
            else:
                if args.get("lineara"):
                    currentDelayedConcentration = float(dose)*(1-IRFrac) / (timeSinceDelayedStart / tmax)
                else:
                    currentDelayedConcentration = getConcentration(float(dose)*(1-IRFrac), t12, timeSinceDelayedStart, tmaxed=False)
        totalConcentration = currentConcentration + currentDelayedConcentration
        totalConcentration = fixForPrecision(totalConcentration)
        print(f"\033[2Kconcentration ({phase}[DR: {delayedPhase}]): {totalConcentration}", end='\r', flush=True)
        checkIfEliminated(totalConcentration, delayedPhase)

def startProbability():
    currentConcentration = dose if startAtCmax else 0
    hasTmaxed = True if startAtCmax else False
    timeSinceTmaxed = None
    tmaxedEpoch = getEpoch(False) if startAtCmax else None
    if args.get("lagtime") != None and usingTimeOrElapse:
        startingEpoch = getStartingTime() + fixTimeUI(getUIValue("lagtime"))
    else:
        startingEpoch = getStartingTime()
    if usingTimeOrElapse:
        tmaxedEpoch = startingEpoch + tmax
    elif startAtCmax:
        tmaxedEpoch = startingEpoch
    while True:
        time.sleep(updateIntervalSeconds)
        timeSinceStart = getEpoch(False) - startingEpoch
        if hasTmaxed == False:
            hasTmaxed = True if timeSinceStart >= tmax else False
            if hasTmaxed:
                if not usingTimeOrElapse:
                    tmaxedEpoch = getEpoch(False)
                currentConcentration = dose
        if hasTmaxed:
            timeSinceTmaxed = getEpoch(False) - tmaxedEpoch
            currentConcentration = getConcentration(dose, t12, timeSinceTmaxed, tmaxed=True) * 100
            currentConcentration = fixForPrecision(currentConcentration)
            print(f"\033[2Kprobability of drug remaining: {currentConcentration}%", end='\r', flush=True)
            checkIfEliminated(currentConcentration)
        else:
            if args.get("lineara"):
                currentConcentration = (timeSinceStart / tmax) * 100
            else:
                currentConcentration = getConcentration(dose, t12a, timeSinceStart, tmaxed=False) * 100
            currentConcentration = fixForPrecision(currentConcentration)
            print(f"\033[2Kconcentration: {currentConcentration}%", end='\r', flush=True)

def startProbabilityDR():
    currentConcentration = float(dose)*IRFrac if startAtCmax else 0
    hasTmaxed = True if startAtCmax else False
    phase = "absorption" if not hasTmaxed else "elimination"
    timeSinceTmaxed = None
    tmaxedEpoch = getEpoch(False) if startAtCmax else None
    delayedTmaxedEpoch = None
    delayedReleaseStarted = False
    timeSinceDelayedTmax = 0
    if args.get("lagtime") != None and usingTimeOrElapse:
        startingEpoch = getStartingTime() + fixTimeUI(getUIValue("lagtime"))
    else:
        startingEpoch = getStartingTime()
    currentDelayedConcentration = 0
    delayedStartingEpoch = startingEpoch + fixTimeUI(getUIValue("dr"))
    if startingEpoch < (DrLagTime + startingEpoch):
        delayedPhase = "lag"
        delayedHasTmaxed = False
    elif startingEpoch < (DrLagTime + startingEpoch + tmax):
        delayedPhase = "absorption"
        delayedHasTmaxed = False
    elif startingEpoch >= (DrLagTime + startingEpoch + tmax):
        delayedPhase = "elimination"
        delayedHasTmaxed = True
    if usingTimeOrElapse:
        tmaxedEpoch = startingEpoch
        delayedTmaxedEpoch = delayedStartingEpoch + tmax
    elif startAtCmax:
        tmaxedEpoch = startingEpoch
    print("\n",end='')
    while True:
        time.sleep(updateIntervalSeconds)
        timeSinceStart = getEpoch(False) - startingEpoch
        timeSinceDelayedStart = getEpoch(False) - delayedStartingEpoch
        if not delayedReleaseStarted:
            delayedReleaseStarted = True if timeSinceStart >= DrLagTime else False
            delayedPhase = "absorption" if delayedReleaseStarted else "lag"
        if not hasTmaxed:
            hasTmaxed = True if timeSinceStart >= tmax else False
            if hasTmaxed:
                phase = "elimination"
                if not usingTimeOrElapse:
                    tmaxedEpoch = getEpoch(False)
                currentConcentration = float(dose)*IRFrac
        if hasTmaxed:
            timeSinceTmaxed = getEpoch(False) - tmaxedEpoch
            currentConcentration = getConcentration(float(dose)*IRFrac, t12, timeSinceTmaxed, tmaxed=True) * 100
        else:
            if args.get("lineara"):
                currentConcentration = (timeSinceStart / tmax) * 100
            else:
                currentConcentration = getConcentration(float(dose)*IRFrac, t12a, timeSinceStart, tmaxed=False) * 100
        if not delayedHasTmaxed:
            delayedHasTmaxed = True if timeSinceStart >= (DrLagTime + tmax) else False
            if delayedHasTmaxed:
                delayedPhase = "elimination"
                if not usingTimeOrElapse:
                    delayedTmaxedEpoch = getEpoch(False)
                currentDelayedConcentration = float(dose)*(1-IRFrac)
        if delayedReleaseStarted:
            if delayedHasTmaxed:
                timeSinceDelayedTmax = getEpoch(False) - delayedTmaxedEpoch
                currentDelayedConcentration = getConcentration(float(dose)*(1-IRFrac), t12, timeSinceDelayedTmax, tmaxed=True) * 100
            else:
                if args.get("lineara"):
                    currentDelayedConcentration = (timeSinceDelayedStart / tmax) * 100
                else:
                    currentDelayedConcentration = getConcentration(float(dose)*(1-IRFrac), t12a, timeSinceDelayedStart, tmaxed=False) * 100
        totalConcentration = fixForPrecision(float(currentConcentration) + float(currentDelayedConcentration))
        currentConcentration = fixForPrecision(float(currentConcentration))
        currentDelayedConcentration = fixForPrecision(float(currentDelayedConcentration))
        if not delayedReleaseStarted:
            if hasTmaxed:
                print(f"\x1b[2Kprobability of drug remaining (IR): {currentConcentration}%", end='\r', flush=True)
            else:
                print(f"\x1b[2Kamount absorbed: {currentConcentration}%", end='\r', flush=True)
        else:
            if hasTmaxed and delayedHasTmaxed:
                print(f"\x1b[1A\x1b[2K\rprobability of drug remaining (IR): {currentConcentration}%\x1b[1B\x1b[2K\rprobability of drug remaining (DR): {currentDelayedConcentration}%", flush=True, end='')
            elif hasTmaxed and not delayedHasTmaxed:
                print(f"\x1b[1A\x1b[2K\rprobability of drug remaining (IR): {currentConcentration}%\x1b[1B\x1b[2K\ramount absorbed (DR): {currentDelayedConcentration}%", flush=True, end='')
            elif not hasTmaxed:
                print(f"\x1b[1A\x1b[2K\rprobability of drug remaining (IR): {currentConcentration}%\x1b[1B\x1b[2K\ramount absorbed (DR): {currentDelayedConcentration}%", flush=True, end='')
        if totalConcentration <= 0 and delayedPhase == "elimination":
            if args.get("autocomplete"):
                raise SystemExit(0)
            else:
                input("\n\nFinished. Press enter to exit")
                raise SystemExit(0)

def startLag():
    lagTime = fixTimeUI( getUIValue("lagtime") )
    if usingTimeOrElapse:
        absorptionPhaseEpoch = getStartingTime() + lagTime
    elif startAtCmax:
        return
    else:
        absorptionPhaseEpoch = lagTime + startingScriptEpoch
    while True:
        time.sleep(updateIntervalSeconds)
        timeUntilAbsorptionPhase = absorptionPhaseEpoch - getEpoch(False)
        if timeUntilAbsorptionPhase <= 0:
            return
        minuteDigits = int(timeUntilAbsorptionPhase // 60)
        secondDigits = int(timeUntilAbsorptionPhase - minuteDigits * 60)
        _timer = f"{minuteDigits}:{secondDigits}"
        print(f"\033[2Klag time remaining: {_timer}", end='\r', flush=True)

method = getMethod()
try:
    startingScriptEpoch = getEpoch()
    currentYear = datetime.datetime.now().year
    currentMonth, currentDay = datetime.datetime.now().month, datetime.datetime.now().day
    currentTime = f"{datetime.datetime.now().hour}:{datetime.datetime.now().minute}:{datetime.datetime.now().second}"
    if args.get("msg") != None:
        print(f"\n{args.get('msg')}")
    print("\nSTART: {}-{}-{} {}\n".format(currentYear, currentMonth, currentDay, currentTime))
    if args.get("lagtime") != None:
        startLag()
    match method:
        case "default":
            if args.get("dr") != None:
                startDefaultDR()
            else:
                startDefault()
        case "linear":
            if args.get("dr") != None:
                startLinearDR()
            else:
                startLinear()
        case "probability":
            if args.get("dr") != None:
                startProbabilityDR()
            else:
                startProbability()
        case _:
            raise SystemExit("method does not exist")
except KeyboardInterrupt:
    print("\n", end='')
    raise SystemExit(0)
except Exception as ERROR:
    raise SystemExit(ERROR)
