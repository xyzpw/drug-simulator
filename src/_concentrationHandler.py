import math
import re
from ._simlogger import *

__all__ = [
    "getConcentration",
    "fixForPrecision",
    "completeScript",
    "checkIfEliminated",
]

def getConcentration(method, dosage, halflife, timeElapsed, hasTmaxed) -> float:
    match method:
        case "default":
            halfLivesPassed = timeElapsed / halflife
            if hasTmaxed:
                return dosage * 0.5**halfLivesPassed
            else:
                return dosage - (dosage * 0.5**halfLivesPassed)
        case "linear":
            ke = math.log(2) / halflife
            fracDose = 1 - (ke * timeElapsed)
            halfLivesPassed = timeElapsed / halflife
            if hasTmaxed:
                return dosage * fracDose
            else:
                return dosage - (dosage * 0.5**halfLivesPassed)
                # return dosage * (timeElapsed / tmax)
        case "probability":
            halfLivesPassed = timeElapsed / halflife
            if hasTmaxed:
                return 0.5**halfLivesPassed
            else:
                return 1 - 0.5**halfLivesPassed

def fixForPrecision(currConcentration: float, currPrecision: int) -> float | int:
    if currPrecision == 0:
        return int(currConcentration)
    if not isinstance(currConcentration, float):
        raise TypeError("fix for precision value must be a float")
    currConcentration = math.floor(currConcentration * 10**currPrecision) / 10**currPrecision
    return currConcentration

def getCompletionMessage(timeToCompletion: float) -> str:
    if timeToCompletion < 60:
        result = "Completion after %d second" % timeToCompletion
        if int(timeToCompletion) != 1: result += "s"
        return result
    daysElapsed = timeToCompletion // 86400
    hoursRemainder = (timeToCompletion - daysElapsed*86400) // 3600
    minutesRemainder = (timeToCompletion - daysElapsed*86400 - hoursRemainder*3600) // 60
    secondsRemainder = timeToCompletion - daysElapsed*86400 - hoursRemainder*3600 - minutesRemainder*60
    result = "Completion after %d day, %d hour, %d minute, and %d second" % (
        daysElapsed,
        hoursRemainder,
        minutesRemainder,
        secondsRemainder
    )
    result = re.sub(r"(?<=\s)0 (?:day|hour|minute|second), (?!and [0-9]*? second)", "", result).replace(", and 0 second", "")
    result = re.sub(r"\s(?P<el>[0-9]{2,}|[2-9]) (?P<unit>day|hour|minute|second)", r" \g<el> \g<unit>s", result)
    result = re.sub(r", (?P<el>[0-9]{2,}|[2-9]) (?P<unit>days?|hours?|minutes?|seconds?)$", r", and \g<el> \g<unit>", result)
    if result.count(",") == 1: result = result.replace(",", "")
    return result

def completeScript(elapsed: bool, autocomplete: int | float):
    print('\n')
    completionMessage = getCompletionMessage(elapsed)
    if autocomplete:
        print(completionMessage)
        raise SystemExit(0)
    input("%s. Press enter to exit" % completionMessage)
    raise SystemExit(0)

def checkIfEliminated(concentration, phase=None, minimum_concentration=None):
    if minimum_concentration == None: minimum_concentration = 0
    if concentration <= minimum_concentration and phase in ["elimination", None, "distribution"]:
        return True
