from time import time as getCurrentEpoch
from time import sleep
from ._concentrationHandler import *
from ._simlogger import *
from ._dosageUnits import *
from ._resultHandler import *

updateIntervalSeconds = 1/20

def initiate(drugInfo, pkInfo):
    tmax, precision = drugInfo.tmax, pkInfo.precision
    t12, t12abs = drugInfo.t12, drugInfo.t12abs
    hasTmaxed = True if pkInfo.startAtCmax else False
    timeSinceTmaxed = None
    tmaxedEpoch = getCurrentEpoch() if pkInfo.startAtCmax else None
    if drugInfo.lagtime != None and pkInfo.usingTimeOrElapse:
        startingEpoch = pkInfo.startingTime + drugInfo.lagtime
    elif drugInfo.lagtime != None and not pkInfo.usingTimeOrElapse:
        startingEpoch = getCurrentEpoch()
    else:
        startingEpoch = pkInfo.startingTime
    if pkInfo.usingTimeOrElapse:
        tmaxedEpoch = startingEpoch + tmax
    elif pkInfo.startAtCmax:
        tmaxedEpoch = startingEpoch
    # loop
    while True:
        sleep(updateIntervalSeconds)
        timeSinceStart = getCurrentEpoch() - startingEpoch
        if not hasTmaxed:
            hasTmaxed = True if timeSinceStart >= tmax else False
            if hasTmaxed:
                if not pkInfo.usingTimeOrElapse:
                    tmaxedEpoch = getCurrentEpoch()
                currentProbability = 100
        if hasTmaxed:
            timeSinceTmaxed = getCurrentEpoch() - tmaxedEpoch
            currentProbability = getConcentration(
                method="probability",
                dosage=1,
                halflife=t12,
                timeElapsed=timeSinceTmaxed,
                hasTmaxed=True,
            )*100
            currentProbability = fixForPrecision(currentProbability, precision)
            resultOutput = probabilityResult(currentProbability, precision, True)
        else:
            if drugInfo.linearabs:
                currentProbability = timeSinceStart / tmax * 100
            else:
                currentProbability = getConcentration(
                    method="probability",
                    dosage=1,
                    halflife=t12abs,
                    timeElapsed=timeSinceStart,
                    hasTmaxed=False,
                )*100
                currentProbability = fixForPrecision(currentProbability, precision)
            resultOutput = probabilityResult(currentProbability, precision, False)
        print("\x1b[2K%s" % resultOutput, end="\r", flush=True)
        if checkIfEliminated(currentProbability):
            timeSinceAdministration = timeSinceStart + drugInfo.lagtime if drugInfo.lagtime != None else float(timeSinceStart)
            completeScript(timeSinceAdministration, pkInfo.autocomplete)

def initiateDR(drugInfo: object, pkInfo: object):
    tmax, t12, t12abs, precision = drugInfo.tmax, drugInfo.t12, drugInfo.t12abs, pkInfo.precision
    hasTmaxed = True if pkInfo.startAtCmax else False
    timeSinceTmaxed = None
    timeSinceDelayedTmax = None
    tmaxedEpoch = getCurrentEpoch() if pkInfo.startAtCmax else None
    if drugInfo.lagtime != None and pkInfo.usingTimeOrElapse:
        startingEpoch = pkInfo.startingTime + drugInfo.lagtime
    elif drugInfo.lagtime != None and not pkInfo.usingTimeOrElapse:
        startingEpoch = getCurrentEpoch()
    else:
        startingEpoch = pkInfo.startingTime
    drLagtime = drugInfo.drLagtime
    delayedStartingEpoch = startingEpoch + drLagtime
    delayedReleaseStarted = getCurrentEpoch() >= delayedStartingEpoch
    delayedHasTmaxed = True if getCurrentEpoch() >= delayedStartingEpoch + tmax else False
    if pkInfo.usingTimeOrElapse:
        tmaxedEpoch = startingEpoch + tmax
        delayedTmaxedEpoch = delayedStartingEpoch + tmax
    elif pkInfo.startAtCmax:
        tmaxedEpoch = startingEpoch
    delayedPhase = "absorption"
    # loop
    print("\n", end="")
    while True:
        sleep(updateIntervalSeconds)
        timeSinceStart = getCurrentEpoch() - startingEpoch
        timeSinceDelayedStart = getCurrentEpoch() - delayedStartingEpoch
        if not delayedReleaseStarted:
            delayedReleaseStarted = True if timeSinceStart >= drLagtime else False
            if delayedReleaseStarted:
                timeSinceDelayedStart = getCurrentEpoch() - delayedStartingEpoch
                delayedPhase = "elimination" if timeSinceDelayedStart >= tmax else "absorption"
        if not hasTmaxed:
            hasTmaxed = True if timeSinceStart >= tmax else False
            if hasTmaxed:
                if not pkInfo.usingTimeOrElapse:
                    tmaxedEpoch = getCurrentEpoch()
                currentProbability = 100
        if hasTmaxed:
            timeSinceTmaxed = getCurrentEpoch() - tmaxedEpoch
            currentProbability = getConcentration(
                method="probability",
                dosage=1,
                halflife=t12,
                timeElapsed=timeSinceTmaxed,
                hasTmaxed=True,
            )*100
        else:
            if drugInfo.linearabs:
                currentProbability = timeSinceStart / tmax * 100
            else:
                currentProbability = getConcentration(
                    method="probability",
                    dosage=1,
                    halflife=t12abs,
                    timeElapsed=timeSinceStart,
                    hasTmaxed=False,
                )*100
        currentProbability = fixForPrecision(currentProbability, precision)
        if delayedReleaseStarted:
            if not delayedHasTmaxed:
                delayedHasTmaxed = True if timeSinceDelayedStart >= tmax else False
                if delayedHasTmaxed:
                    delayedPhase = "elimination"
                    if not pkInfo.usingTimeOrElapse:
                        delayedTmaxedEpoch = getCurrentEpoch()
                    currentDelayedProbability = 100
            if delayedHasTmaxed:
                timeSinceDelayedTmax = getCurrentEpoch() - delayedTmaxedEpoch
                currentDelayedProbability = getConcentration(
                    method="probability",
                    dosage=1,
                    halflife=t12,
                    timeElapsed=timeSinceDelayedTmax,
                    hasTmaxed=True,
                )*100
            else:
                if drugInfo.linearabs:
                    currentDelayedProbability = timeSinceDelayedStart / tmax * 100
                else:
                    currentDelayedProbability = getConcentration(
                        method="probability",
                        dosage=1,
                        halflife=t12abs,
                        timeElapsed=timeSinceDelayedStart,
                        hasTmaxed=False,
                    )*100
            currentDelayedProbability = fixForPrecision(currentDelayedProbability, precision)
        else:
            currentDelayedProbability = 0
        resultOutput = probabilityDrResult(
            currentProbability,
            currentDelayedProbability,
            precision,
            hasTmaxed,
            delayedHasTmaxed
        )
        print("\x1b[1A\r\x1b[2K%s\n\r\x1b[2K%s" % (resultOutput[0], resultOutput[1]), end="", flush=True)
        if checkIfEliminated(currentDelayedProbability, delayedPhase):
            timeSinceAdministration = timeSinceStart + drugInfo.lagtime if drugInfo.lagtime != None else float(timeSinceStart)
            completeScript(timeSinceAdministration, pkInfo.autocomplete)


