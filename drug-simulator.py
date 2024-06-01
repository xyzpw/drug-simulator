#!/usr/bin/env python3

from time import time as getCurrentEpoch
from time import sleep
from datetime import datetime
import traceback
from src import _timeConversions
from src._arghandler import *
from src._uiHandler import *
from src._fileReader import *
from src.promptAuth import *
from src._simlogger import *
from src._dosageUnits import unitToMgFraction
from src import sim_default, sim_linear, sim_probability

myDrug, simInfo = SimulationInfoContainer(), SimulationInfoContainer()

args = vars(createArgs().parse_args())
if args.get("time_format") == "12":
    timeFormat = r"%I:%M:%S %p (%m/%d/%Y)"
elif args.get("time_format") == "24":
    timeFormat = r"%H:%M:%S (%Y-%m-%d)"
else:
    timeFormat = r"%H%M (%Y-%m-%d)"

argFile = args.get("file")
if bool(argFile):
    args = validateFileArgs(argFile, args)
validateArgs(args)
if args.get("bioavailability") == None: args["bioavailability"] = 1.0

useProbability, useLinear, startAtCmax, precision = args.get("probability"), args.get("linear"), args.get("tmaxed"), args.get("precision")
unitPrecision = int(precision)
setattr(simInfo, "useProbability", useProbability)
setattr(simInfo, "useLinear", useLinear)
setattr(simInfo, "startAtCmax", startAtCmax)
setattr(simInfo, "precision", precision)
setattr(simInfo, "unitPrecision", unitPrecision)

def getUIValue(uiTxt, argLocation=None, inputText=None):
    if argLocation == None:
        argLocation = uiTxt
    if inputText == None:
        inputText = uiTxt
    if args.get(argLocation) == None:
        return input(f"{inputText}: ")
    else:
        return args.get(argLocation)

massUnit = None
dose = 1.0
#user input
try:
    if authDosePrompt(useProbability):
        dose, massUnit = fixDose(getUIValue("dose", inputText="dose"))
        dose *= args.get("bioavailability")
        dose *= args.get("count")
        setattr(myDrug, "dose", dose)
        setattr(myDrug, "massUnit", massUnit)

    if authTmaxPrompt(args):
        tmax = fixTmax(getUIValue("tmax", inputText="tmax"), startAtCmax)
        if tmax == float(0): startAtCmax = True
    else:
        tmax = float(0)
    setattr(myDrug, "tmax", tmax)

    if authT12absPrompt(startAtCmax, args.get("linearabs")):
        t12abs = fixT12abs(getUIValue("t12abs", inputText="absorption half-life"))
    else:
        t12abs = None
    setattr(myDrug, "t12abs", t12abs)

    t12 = fixT12(getUIValue("t12", inputText="half-life"))
    setattr(myDrug, "t12", t12)

    distTime = _timeConversions.fixTimeUI(getUIValue("dist_time", inputText="distribution time")) if authDistributionPrompt(args) or args.get("dist_time") != None else None
    t12a = _timeConversions.fixTimeUI(getUIValue("t12a", inputText="distribution half-life")) if authT12aPrompt(args) or args.get("t12a") != None else None
    setattr(myDrug, "distTime", distTime)
    setattr(myDrug, "t12a", t12a)

    if bool(args.get("dr")) and not useProbability:
        IRFrac, DrLagTime = fixDr(
            getUIValue("irfrac", inputText="instant release dose fraction (def. 0.5)"),
            getUIValue("dr")
        )
    elif bool(args.get("dr")) and useProbability:
        IRFrac, DrLagTime = None, _timeConversions.fixTimeUI(getUIValue("dr"))
    else:
        IRFrac, DrLagTime = None, None
    setattr(myDrug, "irFrac", IRFrac)
    setattr(myDrug, "drLagtime", DrLagTime)
except (KeyboardInterrupt, EOFError):
    raise SystemExit(0)
except:
    raise SystemExit(traceback.print_exc())

isBiphasic = True if t12a != None and distTime != None else False
setattr(myDrug, "isBiphasic", isBiphasic)

def getMethod():
    if useProbability:
        return "probability"
    elif useLinear:
        return "linear"
    return "default"

setattr(simInfo, "method", getMethod())

def getStartingTime() -> float:
    if args.get("time"):
        try:
            hour, minute = _timeConversions.getHoursAndMinutesFromReadableTime(str(args.get("time")))
            return _timeConversions.getEpochFromHourAndMinute(hour, minute)
        except:
            raise ValueError("invalid time value")
    elif args.get("elapse") != None:
        try:
            hour, minute = _timeConversions.getHoursAndMinutesFromReadableTime(str(args.get("elapse")))
            return _timeConversions.getEpochFromElapseTime(hour, minute)
        except:
            raise ValueError("invalid elapse value")
    elif args.get("date") != None:
        return _timeConversions.getEpochFromDatetime(args.get("date"))
    return getCurrentEpoch()

setattr(simInfo, "startingTime", getStartingTime())

isBiphasic = t12a != None and distTime != None
usingTimeOrElapse = args.get("time") != None or args.get("elapse") != None or args.get("date") != None
updateIntervalSeconds = 1/20

setattr(simInfo, "isBiphasic", isBiphasic)
setattr(simInfo, "usingTimeOrElapse", usingTimeOrElapse)
setattr(myDrug, "linearabs", args.get("linearabs"))
setattr(simInfo, "autocomplete", args.get("autocomplete"))
setattr(
    simInfo,
    "minimum",
    fixDose(args.get("minimum"))[0] * unitToMgFraction(fixDose(args.get("minimum"))[1]) if args.get("minimum") != None else None
)

def startLag():
    import re
    lagTime = _timeConversions.fixTimeUI( getUIValue("lagtime") )
    setattr(myDrug, "lagtime", lagTime)
    if usingTimeOrElapse:
        absorptionPhaseEpoch = getStartingTime() + lagTime
    elif startAtCmax:
        return
    else:
        absorptionPhaseEpoch = lagTime + startingScriptEpoch
    while True:
        timeUntilAbsorptionPhase = absorptionPhaseEpoch - getCurrentEpoch()
        sleep(updateIntervalSeconds)
        if timeUntilAbsorptionPhase <= 0:
            return
        minuteDigits = int(timeUntilAbsorptionPhase // 60)
        secondDigits = int(timeUntilAbsorptionPhase - minuteDigits * 60)
        if minuteDigits > 0:
            timerOutput = f"{minuteDigits} minutes, {secondDigits} seconds".replace(
                ", 1 seconds", ", 1 second"
            ).replace("1 minutes", "1 minute")
        else:
            timerOutput = "%d seconds" % secondDigits
            timerOutput = re.sub(r"^1 seconds$", "1 second", timerOutput)
        print(f"\033[2Klagtime remaining: {timerOutput}", end='\r', flush=True)

method = getMethod()
try:
    startingScriptEpoch = getCurrentEpoch()
    startingDateOutput = datetime.now().strftime(timeFormat)
    if args.get("msg") != None:
        print("\n%s" % args.get("msg"))
    print("\nSTART: %s\n" % startingDateOutput)
    if args.get("lagtime") != None:
        startLag()
    else:
        setattr(myDrug, "lagtime", None)
    isDelayedRelease = args.get("dr") != None
    if isDelayedRelease: setattr(simInfo, "dr_max", args.get("dr_max"))
    match method:
        case "default":
            if isDelayedRelease:
                sim_default.initiateDR(myDrug, simInfo)
            else:
                sim_default.initiate(myDrug, simInfo)
        case "linear":
            if isDelayedRelease:
                sim_linear.initiateDR(myDrug, simInfo)
            else:
                sim_linear.initiate(myDrug, simInfo)
        case "probability":
            if isDelayedRelease:
                sim_probability.initiateDR(myDrug, simInfo)
            else:
                sim_probability.initiate(myDrug, simInfo)
        case _:
            raise SystemExit("method does not exist")
except KeyboardInterrupt:
    print("\n", end='')
    raise SystemExit(0)
except Exception:
    raise SystemExit(traceback.format_exc())
