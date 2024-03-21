#!/usr/bin/env python3

import time
import datetime
import argparse
import re
import math
import traceback
from src import _timeConversions
from src import _arghandler
from src import _dosageUnits
from src import _resultHandler
from src._uiHandler import *
from src._fileReader import *

parser = argparse.ArgumentParser(
    description="description: Simulates the absorption and elimination of drugs.",
    add_help=False,
)
parser.add_argument("--help", "-h", help="displays help and exits", action="help")
parser.add_argument("--units", help="displays available time units [default: seconds]", action="store_true")
parser.add_argument("--dose", help="the dosage to be simulated", metavar="<dose>[ unit]")
parser.add_argument("--tmax", help="time it takes to reach peak concentration", metavar="<time>[ unit]")
parser.add_argument("--t12abs", help="absorption half-life of the drug to be simulated", metavar="<time>[ unit]")
parser.add_argument("--t12", help="half-life of the drug to be simulated", metavar="<time>[ unit]")
parser.add_argument("--probability", help="display concentration as probability of drug remaining", action="store_true")
parser.add_argument("--linear", help="calculates and uses elimination constant of given half-life", action="store_true")
parser.add_argument("--linearabs", help="uses linear absorption regardless of method", action="store_true")
parser.add_argument("--time", help="time the dose was administered in 24-hour format", metavar="HH:MM")
parser.add_argument("--elapse", help="how much time has passed since the simulation was started", metavar="HH:MM")
parser.add_argument("--tmaxed", help="starts simulation assuming the drug has already peaked", action="store_true")
parser.add_argument("-p", help="decimal places to keep for displayed results", metavar="decimal_precision", dest="precision", default=0)
parser.add_argument("-f", help="bioavailability of the drug being simulated", metavar="decimal", dest="bioavailability")
parser.add_argument("--autocomplete", help="immediately exits once concentration reaches 0", action="store_true")
parser.add_argument("--dr", help="duration until second part of dose is released (delayed release form)", metavar="<time>[ unit]")
parser.add_argument("--irfrac", help="fraction of dose that is instant release (used with dr)", metavar="decimal")
parser.add_argument("--lagtime", help="time taken for drug to appear", metavar="<time>[ unit]")
parser.add_argument("--dr_max", help="displays the maximum achieved concentration since starting the simulation", action="store_true")
parser.add_argument("--clear", help="clears the screen prior to script commencement", action="store_true")
parser.add_argument("--msg", help="custom message on start", metavar="<msg>")
parser.add_argument("--file", help="reads pharmacokinetic information from a json file", metavar="<file_name>")
args = vars(parser.parse_args())
_arghandler.validateArgs(args)
argFile = args.get("file")
if bool(argFile):
    args = validateFileArgs(argFile, args)

useProbability, useLinear, startAtCmax = args.get("probability"), args.get("linear"), args.get("tmaxed")
precision = int(args.get("precision"))
unitPrecision = precision

def getEpoch(asInt=True) -> float | int:
    if asInt:
        return time.time() // 1
    return time.time()

def getUIValue(uiTxt, argLocation=None, inputText=None):
    if bool(argFile):
        phContent = readFile(argFile)
        phResult = phContent.get(uiTxt)
        if phResult != None:
            return phResult
    if argLocation == None:
        argLocation = uiTxt
    if inputText == None:
        inputText = uiTxt
    if args.get(argLocation) == None:
        return input(f"{inputText}: ")
    else:
        return args.get(argLocation)

massUnit = None
# user input
try:
    dose, massUnit = fixDose(getUIValue("dose", inputText="dose"), useProbability)
    if not useProbability and bool(args.get("f")):
        dose = doseWithBioavailability(args.get("f"), dose)
    tmax = fixTmax(getUIValue("tmax", inputText="tmax"), startAtCmax)
    if tmax == float(0): startAtCmax = True
    if not startAtCmax and not args.get("linearabs"):
        t12abs = fixT12abs(getUIValue("t12abs", inputText="absorption half-life"))
    t12 = fixT12(getUIValue("t12", inputText="half-life"))
    if bool(args.get("dr")):
        IRFrac, DrLagTime = fixDr(
            getUIValue("irfrac", inputText="instant release dose fraction (def. 0.5)"),
            getUIValue("dr")
        )
except (KeyboardInterrupt, EOFError):
    raise SystemExit(0)
except Exception as ERROR:
    raise SystemExit(traceback.print_exc())

def getMethod():
    if useProbability:
        return "probability"
    elif useLinear:
        return "linear"
    return "default"

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

def startDefault():
    global massUnit, adjustedConcentration, adjustedPrecision, precision
    if massUnit != None:
        adjustedPrecision = precision
        adjustedConcentration = dose
    currentConcentration = dose if startAtCmax else 0
    hasTmaxed = True if startAtCmax else False
    # skip distribution
    phase = "absorption" if not hasTmaxed else "elimination"
    timeSinceTmax = None
    tmaxedEpoch = None
    if args.get("lagtime") != None and usingTimeOrElapse:
        startingEpoch = getStartingTime() + _timeConversions.fixTimeUI(getUIValue("lagtime"))
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
            if args.get("linearabs"):
                currentConcentration = float(dose) * (timeSinceStart / tmax)
            else:
                currentConcentration = getConcentration(dose, t12abs, timeSinceStart, tmaxed=False)
            currentConcentration = fixForPrecision(currentConcentration)
        if massUnit != None and phase == "elimination":
            adjustedConcentration, massUnit, adjustedPrecision = _dosageUnits.adjustConcentrationFromUnit(currentConcentration, adjustedConcentration, precision, adjustedPrecision, massUnit)
            concentration_response = _resultHandler.defaultResult(phase, adjustedConcentration, adjustedPrecision, massUnit)
            print(f"\033[2K{concentration_response}", end='\r', flush=True)
        elif massUnit != None and phase == "absorption":
            concentration_response = _resultHandler.defaultResult(phase, currentConcentration, precision, massUnit)
            print(f"\033[2K{concentration_response}", end='\r', flush=True)
        else:
            concentration_response = _resultHandler.defaultResult(phase, currentConcentration, precision, massUnit)
            print(f"\033[2K{concentration_response}", end='\r', flush=True)
        checkIfEliminated(currentConcentration, phase)

def startDefaultDR():
    global massUnit, adjustedConcentration, adjustedPrecision, precision
    if massUnit != None:
        adjustedPrecision = precision
        adjustedConcentration = dose
    if args.get("dr_max"):
        DrMaxConcentration = 0
        maxMassUnit = massUnit
    currentConcentration = float(dose)*IRFrac if startAtCmax else 0
    hasTmaxed = True if startAtCmax else False
    phase = "absorption" if not hasTmaxed else "elimination"
    timeSinceTmax = None
    tmaxedEpoch = None
    delayedTmaxEpoch = None
    delayedReleaseStarted = False
    timeSinceDelayedTmax = 0
    if args.get("lagtime") != None and usingTimeOrElapse:
        startingEpoch = getStartingTime() + _timeConversions.fixTimeUI(getUIValue("lagtime"))
    else:
        startingEpoch = getStartingTime()
    currentDelayedConcentration = 0
    delayedStartingEpoch = startingEpoch + _timeConversions.fixTimeUI(getUIValue("dr"))
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
    if args.get("dr_max") and getEpoch() > DrLagTime + startingEpoch:
        raise SystemExit("'dr_max' cannot be used after delayed release has started")
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
            if args.get("linearabs"):
                currentConcentration = float(dose)*IRFrac * (timeSinceStart / tmax)
            else:
                currentConcentration = getConcentration(float(dose)*IRFrac, t12abs, timeSinceStart, tmaxed=False)
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
                if args.get("linearabs"):
                    currentDelayedConcentration = float(dose)*(1-IRFrac) * (timeSinceDelayedStart / tmax)
                else:
                    currentDelayedConcentration = getConcentration(float(dose)*(1-IRFrac), t12abs, timeSinceDelayedStart, tmaxed=False)
        totalConcentration = currentConcentration + currentDelayedConcentration
        totalConcentration = fixForPrecision(totalConcentration)
        if args.get("dr_max"):
            if totalConcentration > DrMaxConcentration:
                DrMaxConcentration = totalConcentration
        if massUnit != None and phase == "elimination" and delayedPhase == "elimination":
            adjustedConcentration, massUnit, adjustedPrecision = _dosageUnits.adjustConcentrationFromUnit(totalConcentration, adjustedConcentration, precision, adjustedPrecision, massUnit)
            if args.get("dr_max"):
                concentration_response = _resultHandler.defaultDrResult(phase, delayedPhase, adjustedConcentration, adjustedPrecision, massUnit, maxMassUnit, DrMaxConcentration)
            else:
                concentration_response = _resultHandler.defaultDrResult(phase, delayedPhase, adjustedConcentration, adjustedPrecision, massUnit)
            print(f"\033[2K{concentration_response}", end='\r', flush=True)
        elif massUnit != None and (phase == "absorption" or delayedPhase in ["absorption", "lag"]):
            if args.get("dr_max"):
                concentration_response = _resultHandler.defaultDrResult(phase, delayedPhase, totalConcentration, precision, massUnit, maxMassUnit, DrMaxConcentration)
            else:
                concentration_response = _resultHandler.defaultDrResult(phase, delayedPhase, totalConcentration, precision, massUnit)
            print(f"\033[2K{concentration_response}", end='\r', flush=True)
        else:
            if args.get("dr_max"):
                concentration_response = _resultHandler.defaultDrResult(phase, delayedPhase, totalConcentration, precision, max_concentration=DrMaxConcentration)
            else:
                concentration_response = _resultHandler.defaultDrResult(phase, delayedPhase, totalConcentration, precision)
            print(f"\033[2K{concentration_response}", end='\r', flush=True)
        checkIfEliminated(totalConcentration, delayedPhase)

def startLinear():
    global massUnit, adjustedConcentration, adjustedPrecision, precision
    currentConcentration = dose if startAtCmax else 0
    if massUnit != None:
        adjustedPrecision = precision
        adjustedConcentration = dose
    hasTmaxed = True if startAtCmax else False
    phase = "absorption" if not hasTmaxed else "elimination"
    timeSinceTmax = None
    tmaxedEpoch = None
    if args.get("lagtime") != None and usingTimeOrElapse:
        startingEpoch = getStartingTime() + _timeConversions.fixTimeUI(getUIValue("lagtime"))
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
            if currentConcentration <= 0:
                currentConcentration = 0
        else:
            if args.get("linearabs"):
                currentConcentration = float(dose) * (timeSinceStart / tmax)
            else:
                currentConcentration = getConcentration(dose, t12abs, timeSinceStart, tmaxed=False)
            currentConcentration = fixForPrecision(currentConcentration)
        if massUnit != None and phase == "elimination":
            adjustedConcentration, massUnit, adjustedPrecision = _dosageUnits.adjustConcentrationFromUnit(currentConcentration, adjustedConcentration, precision, adjustedPrecision, massUnit)
            concentration_response = _resultHandler.defaultResult(phase, adjustedConcentration, adjustedPrecision, massUnit)
            print(f"\033[2K{concentration_response}", end='\r', flush=True)
        elif massUnit != None and phase == "absorption":
            concentration_response = _resultHandler.defaultResult(phase, currentConcentration, precision, massUnit)
            print(f"\033[2K{concentration_response}", end='\r', flush=True)
        else:
            concentration_response = _resultHandler.defaultResult(phase, currentConcentration, precision)
            print(f"\033[2K{concentration_response}", end='\r', flush=True)
        checkIfEliminated(currentConcentration, phase)

def startLinearDR():
    global massUnit, adjustedConcentration, adjustedPrecision, precision
    currentConcentration = float(dose)*IRFrac if startAtCmax else 0
    if massUnit != None:
        adjustedPrecision = precision
        adjustedConcentration = dose
    if args.get("dr_max"):
        DrMaxConcentration = 0
        maxMassUnit = massUnit
    hasTmaxed = True if startAtCmax else False
    phase = "absorption" if not hasTmaxed else "elimination"
    timeSinceTmax = None
    tmaxedEpoch = None
    delayedTmaxEpoch = None
    delayedReleaseStarted = False
    timeSinceDelayedTmax = 0
    if args.get("lagtime") != None and usingTimeOrElapse:
        startingEpoch = getStartingTime() + _timeConversions.fixTimeUI(getUIValue("lagtime"))
    else:
        startingEpoch = getStartingTime()
    currentDelayedConcentration = 0
    delayedStartingEpoch = startingEpoch + _timeConversions.fixTimeUI(getUIValue("dr"))
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
    if args.get("dr_max") and getEpoch() > DrLagTime + startingEpoch:
        raise SystemExit("'dr_max' cannot be used after delayed release has started")
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
            if currentConcentration > 0:
                currentConcentration = getConcentration(float(dose)*IRFrac, t12, timeSinceTmax, tmaxed=True)
            else:
                currentConcentration = 0
        else:
            if args.get("linearabs"):
                currentDelayedConcentration = float(dose)*IRFrac * (timeSinceStart / tmax)
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
                if args.get("linearabs"):
                    currentDelayedConcentration = float(dose)*(1-IRFrac) * (timeSinceDelayedStart / tmax)
                else:
                    currentDelayedConcentration = getConcentration(float(dose)*(1-IRFrac), t12, timeSinceDelayedStart, tmaxed=False)
        totalConcentration = currentConcentration + currentDelayedConcentration
        totalConcentration = fixForPrecision(totalConcentration)
        if args.get("dr_max"):
            if totalConcentration > DrMaxConcentration:
                DrMaxConcentration = totalConcentration
        if massUnit != None and phase == "elimination" and delayedPhase == "elimination":
            adjustedConcentration, massUnit, adjustedPrecision = _dosageUnits.adjustConcentrationFromUnit(totalConcentration, adjustedConcentration, precision, adjustedPrecision, massUnit)
            if args.get("dr_max"):
                concentration_response = _resultHandler.defaultDrResult(phase, delayedPhase, adjustedConcentration, adjustedPrecision, massUnit, maxMassUnit, DrMaxConcentration)
            else:
                concentration_response = _resultHandler.defaultDrResult(phase, delayedPhase, adjustedConcentration, adjustedPrecision, massUnit)
            print(f"\033[2K{concentration_response}", end='\r', flush=True)
        elif massUnit != None and (phase == "absorption" or delayedPhase in ["absorption", "lag"]):
            if args.get("dr_max"):
                concentration_response = _resultHandler.defaultDrResult(phase, delayedPhase, totalConcentration, precision, massUnit, max_concentration=DrMaxConcentration)
            else:
                concentration_response = _resultHandler.defaultDrResult(phase, delayedPhase, totalConcentration, precision, massUnit)
            print(f"\033[2K{concentration_response}", end='\r', flush=True)
        else:
            if args.get("dr_max"):
                concentration_response = _resultHandler.defaultDrResult(phase, delayedPhase, totalConcentration, precision, max_concentration=DrMaxConcentration)
            else:
                concentration_response = _resultHandler.defaultDrResult(phase, delayedPhase, totalConcentration, precision)
            print(f"\033[2K{concentration_response}", end='\r', flush=True)
        checkIfEliminated(totalConcentration, delayedPhase)

def startProbability():
    currentConcentration = dose if startAtCmax else 0
    hasTmaxed = True if startAtCmax else False
    timeSinceTmaxed = None
    tmaxedEpoch = getEpoch(False) if startAtCmax else None
    if args.get("lagtime") != None and usingTimeOrElapse:
        startingEpoch = getStartingTime() + _timeConversions.fixTimeUI(getUIValue("lagtime"))
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
            if args.get("linearabs"):
                currentConcentration = (timeSinceStart / tmax) * 100
            else:
                currentConcentration = getConcentration(dose, t12abs, timeSinceStart, tmaxed=False) * 100
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
        startingEpoch = getStartingTime() + _timeConversions.fixTimeUI(getUIValue("lagtime"))
    else:
        startingEpoch = getStartingTime()
    currentDelayedConcentration = 0
    delayedStartingEpoch = startingEpoch + _timeConversions.fixTimeUI(getUIValue("dr"))
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
            if args.get("linearabs"):
                currentConcentration = (timeSinceStart / tmax) * 100
            else:
                currentConcentration = getConcentration(float(dose)*IRFrac, t12abs, timeSinceStart, tmaxed=False) * 100
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
                if args.get("linearabs"):
                    currentDelayedConcentration = (timeSinceDelayedStart / tmax) * 100
                else:
                    currentDelayedConcentration = getConcentration(float(dose)*(1-IRFrac), t12abs, timeSinceDelayedStart, tmaxed=False) * 100
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
    lagTime = _timeConversions.fixTimeUI( getUIValue("lagtime") )
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
except Exception:
    raise SystemExit(traceback.format_exc())
