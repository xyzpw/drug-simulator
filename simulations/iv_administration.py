from src._necessaryImports import *
from time import (
    sleep,
    time as getCurrentEpoch,
)

__all__ = [
    "simulateIvBolus",
    "simulateIvBolusExcretion",
]

def simulateIvBolus(simInfo: object):
    global updateInterval
    dose, massUnit = simInfo.dose
    precision = simInfo.precision
    t12 = simInfo.t12
    convertedDose, convertedPrecision = float(dose), int(precision)
    convertedMassUnit = str(massUnit)
    while True:
        currentEpoch = getCurrentEpoch()
        timeSinceAppearance = currentEpoch - simInfo.appearanceEpoch
        remainingDose = computeIvDrugContent(dose, timeSinceAppearance, t12)
        convertedDose, convertedMassUnit, convertedPrecision = adjustConcentrationForUnit(
            (remainingDose, convertedDose),
            (massUnit, convertedMassUnit),
            (precision, convertedPrecision),
        )
        result = getDefaultResult(
            "elimination",
            convertedDose if massUnit != None else remainingDose,
            convertedPrecision if massUnit != None else precision,
            convertedMassUnit if massUnit != None else massUnit,
        )
        remainingDoseWithPrecision = getDoseWithPrecision(remainingDose, precision)
        print("\r\x1b[2K%s" % result, end="", flush=True)
        if checkIfEliminated(remainingDoseWithPrecision, "elimination", simInfo.minimum):
            completeScript(timeSinceAppearance)
        sleep(updateInterval)

def simulateIvBolusExcretion(simInfo: object):
    global updateInterval
    dose, massUnit = simInfo.dose
    precision = simInfo.precision
    t12 = simInfo.t12
    excretionFraction = simInfo.excretionUnchanged
    while True:
        currentEpoch = getCurrentEpoch()
        timeSinceAppearance = currentEpoch - simInfo.appearanceEpoch
        remainingDose, currentExcretedDose = computeIvAmountExcreted(
            dose, excretionFraction, t12, timeSinceAppearance
        )
        result = getExcretionResult(
            (currentExcretedDose, massUnit), precision
        )
        remainingDoseWithPrecision = getDoseWithPrecision(remainingDose, precision)
        print("\r\x1b[2K%s" % result, end="", flush=True)
        if checkIfEliminated(remainingDoseWithPrecision, "elimination", simInfo.minimum):
            completeScript(timeSinceAppearance)
        sleep(updateInterval)
