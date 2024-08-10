from time import (
    time as getCurrentEpoch,
    sleep,
)
from src._necessaryImports import *

__all__ = [
    "simulateCustomAdministration",
    "simulateCustomDrAdministration",
]

def _checkIsBiphasic(simObject):
    return True in [hasattr(simObject, i) for i in ["t12a", "dist_time", "biphasic"]]

def simulateCustomAdministration(simInfo: object):
    global updateInterval
    dose, massUnit = simInfo.dose
    if hasattr(simInfo, "bioavailability"):
        dose *= simInfo.bioavailability
    convertedDose, convertedMassUnit = float(dose), str(massUnit)
    precision = simInfo.precision
    convertedPrecision = int(precision)
    t12 = simInfo.t12
    cmaxEpoch = simInfo.appearanceEpoch + simInfo.tmax
    hasTmaxed = False
    phase = "absorption"
    isBiphasic = _checkIsBiphasic(simInfo)
    if isBiphasic:
        doseAfterDistribution = pow(1/2, simInfo.dist_time / simInfo.t12a) * dose
    while True:
        currentEpoch = getCurrentEpoch()
        timeSinceDose = currentEpoch - simInfo.doseEpoch
        timeSinceAppearance = currentEpoch - simInfo.appearanceEpoch
        timeSinceTmax = (currentEpoch - cmaxEpoch) if phase in ["elimination", "distribution"] else 0
        if not hasTmaxed:
            hasTmaxed = timeSinceAppearance >= simInfo.tmax
            if hasTmaxed:
                currentDose = float(dose)
                phase = "elimination" if not isBiphasic else "distribution"
        if isBiphasic and phase == "distribution":
            if timeSinceTmax >= simInfo.dist_time:
                phase = "elimination"
        if hasTmaxed:
            currentDose = computeIvDrugContent(
                dose if phase == "distribution" else doseAfterDistribution,
                timeSinceTmax - simInfo.dist_time if phase == "elimination" else timeSinceTmax,
                simInfo.t12a if phase == "distribution" else t12,
            ) if isBiphasic else computeIvDrugContent(dose, timeSinceTmax, t12)
        else:
            currentDose = computeAbsorbedDose(
                dose, timeSinceAppearance, simInfo.t12abs
            ) if not hasattr(simInfo, "linearabs") else computeLinearAbsorbed(dose, simInfo.tmax, timeSinceAppearance)
        currentDoseWithPrecision = getDoseWithPrecision(currentDose, precision)
        if phase == "elimination" and massUnit != None:
            convertedDose, convertedMassUnit, convertedPrecision = adjustConcentrationForUnit(
                (currentDose, convertedDose),
                (massUnit, convertedMassUnit),
                (precision, convertedPrecision),
            )
            result = getDefaultResult(
                phase,
                convertedDose,
                convertedPrecision,
                convertedMassUnit,
            )
        else:
            result = getDefaultResult(
                phase,
                currentDose,
                precision,
                massUnit,
            )
        print("\r\x1b[2K%s" % result, end="", flush=True)
        if checkIfEliminated(currentDoseWithPrecision, phase, simInfo.minimum):
            completeScript(timeSinceDose)
        sleep(updateInterval)

def simulateCustomDrAdministration(simInfo: object):
    global updateInterval
    dose, massUnit = simInfo.dose
    if hasattr(simInfo, "bioavailability"):
        dose *= simInfo.bioavailability
    irDose, drDose = simInfo.irfrac * dose, (1 - simInfo.irfrac) * dose
    drLagtime = simInfo.dr
    irCmaxEpoch = simInfo.appearanceEpoch + simInfo.tmax
    drCmaxEpoch = irCmaxEpoch + drLagtime
    irPhase, drPhase = "absorption", "lag"
    convertedTotalDose, convertedMassUnit = float(irDose), str(massUnit)
    precision = simInfo.precision
    convertedPrecision = int(precision)
    t12 = simInfo.t12
    irHasTmaxed, drHasTmaxed = False, False
    isBiphasic = _checkIsBiphasic(simInfo)
    peakDose = 0
    drHasReleased = False
    if isBiphasic:
        irDoseAfterDistribution = pow(1/2, simInfo.dist_time / simInfo.t12a) * irDose
        drDoseAfterDistribution = pow(1/2, simInfo.dist_time / simInfo.t12a) * drDose
    while True:
        currentEpoch = getCurrentEpoch()
        timeSinceIrDose = currentEpoch - simInfo.doseEpoch
        timeSinceDrDose = timeSinceIrDose + drLagtime
        timeSinceIrAppearance = currentEpoch - simInfo.appearanceEpoch
        timeSinceDrAppearance = timeSinceIrAppearance - drLagtime if drHasReleased else 0
        timeSinceIrTmax = currentEpoch - irCmaxEpoch if irPhase in ["elimination", "distribution"] else 0
        timeSinceDrTmax = currentEpoch - drCmaxEpoch if drPhase in ["elimination", "distribution"] else 0
        if not drHasReleased:
            drHasReleased = timeSinceIrAppearance >= drLagtime
        if not irHasTmaxed:
            irHasTmaxed = currentEpoch >= irCmaxEpoch
            if irHasTmaxed:
                irPhase = "distribution" if isBiphasic else "elimination"
                irCurrentDose = float(irDose) if irPhase == "elimination" else float(irDoseAfterDistribution)
        if not drHasTmaxed:
            drHasTmaxed = currentEpoch >= drCmaxEpoch
            if drHasTmaxed:
                drPhase = "distribution" if isBiphasic else "elimination"
                drCurrentDose = float(dose) if drPhase == "elimination" else float(drDoseAfterDistribution)
        if isBiphasic and irPhase == "distribution":
            if timeSinceIrTmax >= simInfo.dist_time:
                irPhase = "elimination"
        if isBiphasic and drPhase == "distribution":
            if timeSinceDrTmax >= simInfo.dist_time:
                drPhase = "elimination"
        # calculating dose
        if irHasTmaxed:
            irCurrentDose = computeIvDrugContent(
                irDose if irPhase == "distribution" else irDoseAfterDistribution,
                (timeSinceIrTmax - simInfo.dist_time) if irPhase == "elimination" else timeSinceIrTmax,
                t12 if irPhase == "elimination" else simInfo.t12a,
            ) if isBiphasic else computeIvDrugContent(irDose, timeSinceIrTmax, t12)
        else:
            irCurrentDose = computeAbsorbedDose(
                irDose, timeSinceIrAppearance, simInfo.t12abs
            ) if not hasattr(simInfo, "linearabs") else computeLinearAbsorbed(irDose, simInfo.tmax, timeSinceIrAppearance)
        # calculating delayed release
        if drHasTmaxed:
            drCurrentDose = computeIvDrugContent(
                drDose if drPhase == "distribution" else drDoseAfterDistribution,
                (timeSinceDrTmax - simInfo.dist_time) if drPhase == "elimination" else timeSinceDrTmax,
                t12 if drPhase == "elimination" else simInfo.t12a
            ) if isBiphasic else computeIvDrugContent(drDose, timeSinceDrAppearance, t12)
        else:
            drCurrentDose = computeAbsorbedDose(
                drDose, timeSinceDrAppearance, simInfo.t12abs
            ) if not hasattr(simInfo, "linearabs") else computeLinearAbsorbed(drDose, simInfo.tmax, timeSinceDrAppearance)
        currentDoseTotal = irCurrentDose + drCurrentDose
        currentDoseTotalWithPrecision = getDoseWithPrecision(currentDoseTotal, precision)
        if currentDoseTotal > peakDose:
            peakDose = float(currentDoseTotal)
        # Don't use converted mass unit if elimination phase has not been reached
        if drPhase == "elimination" and massUnit != None:
            convertedTotalDose, convertedMassUnit, convertedPrecision = adjustConcentrationForUnit(
                (currentDoseTotal, convertedTotalDose),
                (massUnit, convertedMassUnit),
                (precision, convertedPrecision),
            )
            result = getDefaultDrResult(
                convertedTotalDose,
                peakDose if hasattr(simInfo, "dr_max") else None,
                (convertedPrecision, precision),
                (convertedMassUnit, massUnit),
                (irPhase, drPhase),
            )
        else:
            result = getDefaultDrResult(
                currentDoseTotal,
                peakDose if hasattr(simInfo, "dr_max") else None,
                (precision, precision),
                (massUnit, massUnit),
                (irPhase, drPhase),
            )
        print("\r\x1b[2K%s" % result, end='', flush=True)
        if checkIfEliminated(currentDoseTotalWithPrecision, drPhase, simInfo.minimum):
            completeScript(timeSinceIrDose)
        sleep(updateInterval)

