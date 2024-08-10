from src._necessaryImports import *
from time import (
    sleep,
    time as getCurrentEpoch,
)

__all__ = [
    "simulateCustomDecayProbability",
    "simulateCustomDrDecayProbability",
]

def simulateCustomDecayProbability(simInfo: object):
    global updateInterval
    t12 = simInfo.t12
    precision = simInfo.precision
    remainProbability = 1
    fractionAbsorbed = 0
    epochAtTmax = simInfo.appearanceEpoch + simInfo.tmax
    hasTmaxed = getCurrentEpoch() >= epochAtTmax
    phase = "absorption"
    while True:
        currentEpoch = getCurrentEpoch()
        timeSinceDose = currentEpoch - simInfo.doseEpoch
        timeSinceAppearance = currentEpoch - simInfo.appearanceEpoch
        timeSinceTmax = currentEpoch - epochAtTmax if hasTmaxed else 0
        if not hasTmaxed:
            hasTmaxed = currentEpoch >= epochAtTmax
            if hasTmaxed:
                phase = "elimination"
                remainProbability = 1
                fractionAbsorbed = 1
        if hasTmaxed:
            remainProbability = computeRetentionProbability(timeSinceTmax, t12)
        else:
            fractionAbsorbed = computeAbsorbedDose(
                1, timeSinceAppearance, simInfo.t12abs
            ) if not hasattr(simInfo, "linearabs") else computeLinearAbsorbed(
                1, simInfo.tmax, timeSinceAppearance
            )
        result = getProbabilityResult(
            fractionAbsorbed if not hasTmaxed else remainProbability,
            precision,
            hasTmaxed,
        )
        print("\r\x1b[2K%s" % result, end="", flush=True)
        if checkIfEliminated(
            int(remainProbability * pow(10, precision + 2)),
            phase,
            simInfo.minimum * pow(10, precision + 2),
        ):
            completeScript(timeSinceDose)
        sleep(updateInterval)

def simulateCustomDrDecayProbability(simInfo: object):
    global updateInterval
    t12 = simInfo.t12
    precision = simInfo.precision
    irRemainProbability, drRemainProbability = 1, 1
    irAbsorbedFraction, drAbsorbedFraction = 0, 0
    drLagtime = simInfo.dr
    epochAtIrTmax = simInfo.appearanceEpoch + simInfo.tmax
    epochAtDrTmax = epochAtIrTmax + drLagtime
    irHasTmaxed, drHasTmaxed = getCurrentEpoch() >= epochAtIrTmax, getCurrentEpoch() >= epochAtDrTmax
    irPhase, drPhase = "elimination", "lag"
    drHasReleased = False
    print("\n", end="")
    while True:
        currentEpoch = getCurrentEpoch()
        timeSinceDose = currentEpoch - simInfo.doseEpoch
        timeSinceIrAppearance = currentEpoch - simInfo.appearanceEpoch
        timeSinceDrAppearance = timeSinceIrAppearance - drLagtime if drHasReleased else 0
        timeSinceIrTmax = currentEpoch - epochAtIrTmax if irHasTmaxed else 0
        timeSinceDrTmax = currentEpoch - epochAtDrTmax if drHasTmaxed else 0
        if not drHasReleased and timeSinceDose >= drLagtime:
            drHasReleased = True
            drPhase = "absorption"
        if not irHasTmaxed:
            irHasTmaxed = currentEpoch >= epochAtIrTmax
            if irHasTmaxed:
                irPhase = "elimination"
                irRemainProbability = 1
        if not drHasTmaxed:
            drHasTmaxed = currentEpoch >= epochAtDrTmax
            if drHasTmaxed:
                drPhase = "elimination"
                drRemainProbability = 1
        if irHasTmaxed:
            irRemainProbability = computeRetentionProbability(timeSinceIrTmax, t12)
        else:
            irAbsorbedFraction = computeAbsorbedDose(
                1, timeSinceIrAppearance, simInfo.t12abs,
            ) if not hasattr(simInfo, "linearabs") else computeLinearAbsorbed(
                1, simInfo.tmax, timeSinceIrAppearance)
        if drHasTmaxed:
            drRemainProbability = computeRetentionProbability(timeSinceDrTmax, t12)
        elif drPhase == "absorption":
            drAbsorbedFraction = computeAbsorbedDose(
                1, timeSinceDrAppearance, simInfo.t12abs,
            ) if not hasattr(simInfo, "linearabs") else computeLinearAbsorbed(
                1, simInfo.tmax, timeSinceDrAppearance)
        irResult, drResult = getProbabilityDrResult(
            (irRemainProbability if irHasTmaxed else irAbsorbedFraction,
            drRemainProbability if drHasTmaxed else drAbsorbedFraction),
            (precision, precision),
            (irHasTmaxed, drHasTmaxed)
        )
        print("\x1b[1A\r\x1b[2K%s\x1b[1B\r\x1b[2K%s" % (irResult, drResult), end="", flush=True)
        if checkIfEliminated(
            int(drRemainProbability * pow(10, precision + 2)),
            drPhase,
            simInfo.minimum * pow(10, precision + 2),
        ):
            completeScript(timeSinceDose)
        sleep(updateInterval)
