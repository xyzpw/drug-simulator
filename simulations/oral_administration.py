from time import (
    time as getCurrentEpoch,
    sleep,
)
from src._necessaryImports import *

__all__ = [
    "simulateOralAdministration",
    "simulateDrOralAdministration",
    "simulateProdrugOralAdministration",
    "simulateOralAdministrationExcretion",
]

def simulateOralAdministration(simInfo: object):
    global updateInterval
    startingEpoch = simInfo.doseEpoch
    appearanceEpoch = simInfo.appearanceEpoch
    dose, massUnit = simInfo.dose
    convertedDose, convertedMassUnit = float(dose), str(massUnit) if massUnit != None else None
    t12, t12abs = simInfo.t12, simInfo.t12abs
    precision = simInfo.precision
    convertedPrecision = int(precision)
    while True:
        timeSinceAppearance = getCurrentEpoch() - appearanceEpoch
        timeSinceAdministration = getCurrentEpoch() - startingEpoch
        currentConcentration = computeOralDrugContent(
            dose,
            simInfo.bioavailability,
            (simInfo.t12abs, simInfo.t12),
            timeSinceAppearance,
        ); concentrationWithPrecision = getDoseWithPrecision(currentConcentration, precision)
        phase = computeOralRoutePhase((t12abs, t12), timeSinceAppearance)
        if phase == "elimination" and massUnit != None:
            convertedDose, convertedMassUnit, convertedPrecision = adjustConcentrationForUnit(
                (concentrationWithPrecision, convertedDose),
                (massUnit, convertedMassUnit),
                (precision, convertedPrecision),
            )
            resultOutput = getDefaultResult(
                phase,
                convertedDose,
                convertedPrecision,
                convertedMassUnit,
            )
        else:
            resultOutput = getDefaultResult(
                phase,
                currentConcentration,
                precision,
                massUnit,
            )
        print("\r\x1b[2K%s" % resultOutput, end="", flush=True)
        if checkIfEliminated(concentrationWithPrecision, phase, simInfo.minimum):
            completeScript(timeSinceAdministration)
        sleep(updateInterval)

def simulateOralAdministrationExcretion(simInfo: object):
    global updateInterval
    dose, massUnit = simInfo.dose
    precision = simInfo.precision
    t12, t12abs = simInfo.t12, simInfo.t12abs
    excretionFraction = simInfo.excretionUnchanged
    while True:
        currentEpoch = getCurrentEpoch()
        timeSinceAppearance = currentEpoch - simInfo.appearanceEpoch
        excretedDose = computeOralAmountEliminated(
            dose, simInfo.bioavailability, (t12abs, t12), timeSinceAppearance
        ) * excretionFraction
        currentDose = computeOralDrugContent(
            dose, simInfo.bioavailability, (t12abs, t12), timeSinceAppearance
        )
        currentDoseWithPrecision = getDoseWithPrecision(currentDose, precision)
        result = getExcretionResult(
            (excretedDose, massUnit), precision
        )
        phase = computeOralRoutePhase((t12abs, t12), timeSinceAppearance)
        print("\r\x1b[2K%s" % result, end="", flush=True)
        if checkIfEliminated(currentDoseWithPrecision, phase, simInfo.minimum):
            completeScript(timeSinceAppearance)
        sleep(updateInterval)

def simulateDrOralAdministration(simInfo: object):
    global updateInterval
    drLagtime = simInfo.dr
    doseEpoch = simInfo.doseEpoch
    irAppearanceEpoch = simInfo.appearanceEpoch
    drAppearanceEpoch = doseEpoch + drLagtime
    t12abs, t12 = simInfo.t12abs, simInfo.t12
    dose, massUnit = simInfo.dose
    convertedMassUnit = str(massUnit) if massUnit != None else None
    precision = simInfo.precision
    convertedPrecision = int(precision)
    irDose, drDose = dose * simInfo.irfrac, dose * (1 - simInfo.irfrac)
    highestDoseAchieved = 0
    convertedTotalDoseRemaining = float(irDose)
    while True:
        timeSinceIrAppearance = getCurrentEpoch() - irAppearanceEpoch
        timeSinceDrAppearance = getCurrentEpoch() - drAppearanceEpoch
        timeSinceDose = getCurrentEpoch() - doseEpoch
        timeSinceDrDose = getCurrentEpoch() - (doseEpoch + drLagtime)
        irDoseRemaining, drDoseRemaining = computeDrOralDrugContent(
            (irDose, drDose),
            simInfo.bioavailability,
            (t12abs, t12),
            (timeSinceIrAppearance, timeSinceDrAppearance),
        )
        totalDoseRemaining = irDoseRemaining + drDoseRemaining
        if highestDoseAchieved < totalDoseRemaining:
            highestDoseAchieved = float(totalDoseRemaining)
        totalDoseRemainingWithPrecision = getDoseWithPrecision(totalDoseRemaining, precision)
        irPhase, drPhase = computeOralRoutePhase((t12abs, t12), timeSinceIrAppearance), computeOralRoutePhase((t12abs, t12), timeSinceDrAppearance)
        if drPhase == "elimination" and (massUnit != None and convertedMassUnit != None):
            convertedTotalDoseRemaining, convertedMassUnit, convertedPrecision = adjustConcentrationForUnit(
                (totalDoseRemaining, convertedTotalDoseRemaining),
                (massUnit, convertedMassUnit),
                (precision, convertedPrecision),
            )
            resultOutput = getDefaultDrResult(
                convertedTotalDoseRemaining,
                highestDoseAchieved if hasattr(simInfo, "dr_max") else None,
                (convertedPrecision, precision),
                (convertedMassUnit, massUnit),
                (irPhase, drPhase),
            )
        else:
            resultOutput = getDefaultDrResult(
                totalDoseRemaining,
                highestDoseAchieved if hasattr(simInfo, "dr_max") else None,
                (precision, precision),
                (massUnit, massUnit),
                (irPhase, drPhase),
            )
        print("\r\x1b[2K%s" % resultOutput, end="", flush=True)
        if checkIfEliminated(totalDoseRemainingWithPrecision, drPhase, simInfo.minimum):
            completeScript(timeSinceDose)
        sleep(updateInterval)

def simulateProdrugOralAdministration(simInfo: object):
    global updateInterval
    dose, massUnit = simInfo.dose
    precision = simInfo.precision
    prodrugT12 = simInfo.t12
    prodrugT12abs = simInfo.t12abs
    activeDrugT12 = simInfo.activeT12
    prodrugPhase = "absorption"
    while True:
        currentEpoch = getCurrentEpoch()
        timeSinceDose = currentEpoch - simInfo.doseEpoch
        timeSinceAppearance = currentEpoch - simInfo.appearanceEpoch
        remainingProdrug, remainingActiveDrug = computeOralProdrugConcentrations(
            dose, (prodrugT12abs, prodrugT12, activeDrugT12),
            (simInfo.bioavailability, simInfo.prodrug), timeSinceAppearance
        )
        if prodrugPhase != "elimination":
            prodrugPhase = computeOralRoutePhase((prodrugT12abs, prodrugT12), timeSinceAppearance)
        prodrugWithPrecision = getDoseWithPrecision(remainingProdrug, precision)
        doseWithPrecision = getDoseWithPrecision(remainingActiveDrug, precision)
        result = getOralProdrugResult(
            (remainingProdrug, remainingActiveDrug),
            precision, massUnit,
            checkIfEliminated(prodrugWithPrecision, prodrugPhase, 0)
        )
        print("\r\x1b[2K%s" % result, end='', flush=True)
        if checkIfEliminated(doseWithPrecision, prodrugPhase, simInfo.minimum):
            completeScript(timeSinceDose)
        sleep(updateInterval)
