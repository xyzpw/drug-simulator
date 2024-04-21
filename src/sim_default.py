from time import time as getCurrentEpoch
from time import sleep
from . import variables
from ._concentrationHandler import *
from ._simlogger import *
from ._dosageUnits import *
from ._resultHandler import *

updateIntervalSeconds = 1/20

def initiate(drugInfo: object, pkInfo: object):
    infoContainer = InfoFetcher(drugInfo, pkInfo)
    dose, massUnit, precision, isBiphasic = infoContainer.getMainValues()
    currentConcentration = 0
    adjustedPrecision, adjustedConcentration = int(precision), float(dose)
    tmax, hasTmaxed, phase, timeSinceTmax, tmaxedEpoch = infoContainer.getPeakAndPhaseValues()
    t12, t12a, t12abs = drugInfo.t12, drugInfo.t12a, drugInfo.t12abs
    if drugInfo.lagtime != None and pkInfo.usingTimeOrElapse:
        startingEpoch = pkInfo.startingTime + drugInfo.lagtime
    elif drugInfo.lagtime != None and not pkInfo.usingTimeOrElapse:
        startingEpoch = getCurrentEpoch()
    else:
        startingEpoch = pkInfo.startingTime
    if pkInfo.usingTimeOrElapse:
        tmaxedEpoch = startingEpoch + tmax
        if isBiphasic:
            if tmaxedEpoch < drugInfo.distTime + tmaxedEpoch and hasTmaxed:
                phase = "distribution"
    elif pkInfo.startAtCmax:
        tmaxedEpoch = float(startingEpoch)
    if isBiphasic:
        concentrationAfterDistribution = getConcentration(
            method="default",
            dosage=dose,
            halflife=t12a,
            timeElapsed=drugInfo.distTime,
            hasTmaxed=True
        )
    # loop
    while True:
        sleep(updateIntervalSeconds)
        timeSinceStart = getCurrentEpoch() - startingEpoch
        if not hasTmaxed:
            hasTmaxed = True if timeSinceStart >= tmax else False
            if hasTmaxed:
                phase = "elimination"
                if not pkInfo.usingTimeOrElapse:
                    tmaxedEpoch = getCurrentEpoch()
                currentConcentration = float(dose)
        currentT12 = variables.getT12(phase, t12, t12abs, t12a)
        if hasTmaxed:
            timeSinceTmax = getCurrentEpoch() - tmaxedEpoch
            if isBiphasic:
                if timeSinceTmax <= drugInfo.distTime:
                    phase = "distribution"
                    currentConcentration = getConcentration(
                        method="default",
                        dosage=dose,
                        halflife=currentT12,
                        timeElapsed=timeSinceTmax,
                        hasTmaxed=True,
                    )
                else:
                    phase = "elimination"
                    dose = concentrationAfterDistribution
                    currentConcentration = getConcentration(
                        method="default",
                        dosage=dose,
                        halflife=t12,
                        timeElapsed=timeSinceTmax,
                        hasTmaxed=True,
                    )
            else:
                currentConcentration = getConcentration(
                    method="default",
                    dosage=dose,
                    halflife=currentT12,
                    timeElapsed=timeSinceTmax,
                    hasTmaxed=True,
                )
            currentConcentration = fixForPrecision(currentConcentration, precision)
        else:
            if drugInfo.linearabs:
                currentConcentration = (timeSinceStart / tmax) * dose
            else:
                currentConcentration = getConcentration(
                    method="default",
                    dosage=dose,
                    halflife=currentT12,
                    timeElapsed=timeSinceStart,
                    hasTmaxed=False,
                )
            currentConcentration = fixForPrecision(currentConcentration, precision)
        if massUnit != None and phase == "elimination":
            adjustedConcentration, massUnit, adjustedPrecision = adjustConcentrationFromUnit(currentConcentration, adjustedConcentration, precision, adjustedPrecision, massUnit)
            concentration_response = defaultResult(phase, adjustedConcentration, adjustedPrecision, massUnit)
        elif massUnit != None and phase in ["absorption", "distribution"]:
            concentration_response = defaultResult(phase, currentConcentration, precision, massUnit)
        else:
            concentration_response = defaultResult(phase, currentConcentration, precision, massUnit)
        print("\x1b[2K%s" % concentration_response, end="\r", flush=True)
        if checkIfEliminated(currentConcentration, phase):
            timeSinceAdministration = timeSinceStart + drugInfo.lagtime if drugInfo.lagtime != None else float(timeSinceStart)
            completeScript(timeSinceAdministration, pkInfo.autocomplete)


def initiateDR(drugInfo: object, pkInfo: object) -> None:
    infoContainer = InfoFetcher(drugInfo, pkInfo)
    dose, massUnit, precision, isBiphasic = infoContainer.getMainValues()
    maxMassUnit = str(massUnit)
    irDose, drDose = dose * drugInfo.irFrac, dose * (1 - drugInfo.irFrac)
    drMaxConcentration = 0
    maxMassUnit = str(massUnit)
    currentConcentration, currentDelayedConcentration = 0, 0
    adjustedPrecision, adjustedConcentration = pkInfo.precision, drugInfo.dose
    tmax, hasTmaxed, phase, timeSinceTmax, tmaxedEpoch = infoContainer.getPeakAndPhaseValues()
    t12, t12a, t12abs = drugInfo.t12, drugInfo.t12a, drugInfo.t12abs
    if drugInfo.lagtime != None and pkInfo.usingTimeOrElapse:
        startingEpoch = pkInfo.startingTime + drugInfo.lagtime
    elif drugInfo.lagtime != None and not pkInfo.usingTimeOrElapse:
        startingEpoch = getCurrentEpoch()
    else:
        startingEpoch = pkInfo.startingTime
    delayedPhase, delayedHasTmaxed, delayedReleaseStarted, drLagtime = infoContainer.getDrPhaseValues(startingEpoch)
    delayedStartingEpoch = startingEpoch + drLagtime
    if pkInfo.usingTimeOrElapse:
        tmaxedEpoch = startingEpoch + tmax
        delayedTmaxedEpoch = delayedStartingEpoch + tmax
        if isBiphasic:
            if tmaxedEpoch < drugInfo.distTime + tmaxedEpoch and hasTmaxed:
                phase = "distribution"
    elif pkInfo.startAtCmax:
        tmaxedEpoch = float(startingEpoch)
    if isBiphasic:
        irConcentrationAfterDistribution = getConcentration(
            method="default",
            dosage=irDose,
            halflife=t12a,
            timeElapsed=drugInfo.distTime,
            hasTmaxed=True,
        )
        drConcentrationAfterDistribution = getConcentration(
            method="default",
            dosage=drDose,
            halflife=t12a,
            timeElapsed=drugInfo.distTime,
            hasTmaxed=True,
        )
    # loop
    while True:
        sleep(updateIntervalSeconds)
        timeSinceStart = getCurrentEpoch() - startingEpoch
        timeSinceDelayedStart = getCurrentEpoch() - delayedStartingEpoch
        if not delayedReleaseStarted:
            delayedReleaseStarted = True if timeSinceStart >= drLagtime else False
            if delayedReleaseStarted:
                timeSinceDelayedStart = getCurrentEpoch() - delayedStartingEpoch
                if timeSinceDelayedStart < tmax:
                    delayedPhase = "absorption"
        if not hasTmaxed:
            hasTmaxed = True if timeSinceStart >= tmax else False
            if hasTmaxed:
                phase = "elimination"
                if not pkInfo.usingTimeOrElapse:
                    tmaxedEpoch = getCurrentEpoch()
                currentConcentration = float(irDose)
        currentT12 = variables.getT12(phase, t12, t12abs, t12a)
        if not delayedHasTmaxed:
            delayedHasTmaxed = True if timeSinceDelayedStart >= tmax else False
            if delayedHasTmaxed:
                delayedPhase = "elimination"
                if not pkInfo.usingTimeOrElapse:
                    delayedTmaxedEpoch = getCurrentEpoch()
                currentDelayedConcentration = float(drDose)

        currentDelayedT12 = variables.getT12(delayedPhase, t12, t12abs, t12a)
        if hasTmaxed:
            timeSinceTmax = getCurrentEpoch() - tmaxedEpoch
            if isBiphasic:
                if timeSinceTmax <= drugInfo.distTime:
                    phase = "distribution"
                    currentConcentration = getConcentration(
                        method="default",
                        dosage=irDose,
                        halflife=currentT12,
                        timeElapsed=timeSinceTmax,
                        hasTmaxed=True,
                    )
                else:
                    phase = "elimination"
                    irDose = irConcentrationAfterDistribution
                    currentConcentration = getConcentration(
                        method="default",
                        dosage=irDose,
                        halflife=t12,
                        timeElapsed=timeSinceTmax,
                        hasTmaxed=True,
                    )
            else:
                currentConcentration = getConcentration(
                    method="default",
                    dosage=irDose,
                    halflife=currentT12,
                    timeElapsed=timeSinceTmax,
                    hasTmaxed=True,
                )
        else:
            if drugInfo.linearabs:
                currentConcentration = (timeSinceStart / tmax) * irDose
            else:
                currentConcentration = getConcentration(
                    method="default",
                    dosage=irDose,
                    halflife=currentT12,
                    timeElapsed=timeSinceStart,
                    hasTmaxed=False,
                )
        if delayedReleaseStarted:
            if delayedHasTmaxed:
                timeSinceDelayedTmax = getCurrentEpoch() - delayedTmaxedEpoch
                if isBiphasic:
                    if timeSinceDelayedTmax <= drugInfo.distTime:
                        delayedPhase = "distribution"
                        currentDelayedConcentration = getConcentration(
                            method="default",
                            dosage=drDose,
                            halflife=currentDelayedT12,
                            timeElapsed=timeSinceDelayedTmax,
                            hasTmaxed=True,
                        )
                    else:
                        delayedPhase = "elimination"
                        drDose = drConcentrationAfterDistribution
                        currentDelayedConcentration = getConcentration(
                            method="default",
                            dosage=drDose,
                            halflife=t12,
                            timeElapsed=timeSinceDelayedTmax,
                            hasTmaxed=True,
                        )
                else:
                    currentDelayedConcentration = getConcentration(
                        method="default",
                        dosage=drDose,
                        halflife=currentDelayedT12,
                        timeElapsed=timeSinceDelayedTmax,
                        hasTmaxed=True
                    )
            else:
                if drugInfo.linearabs:
                    currentDelayedConcentration = (timeSinceDelayedStart / tmax) * drDose
                else:
                    currentDelayedConcentration = getConcentration(
                        method="default",
                        dosage=drDose,
                        halflife=currentDelayedT12,
                        timeElapsed=timeSinceDelayedStart,
                        hasTmaxed=False,
                    )
        totalConcentration = currentConcentration + currentDelayedConcentration
        totalConcentration = fixForPrecision(totalConcentration, precision)
        if pkInfo.dr_max:
            if totalConcentration > drMaxConcentration:
                drMaxConcentration = float(totalConcentration)
        if massUnit != None and phase == "elimination" and delayedPhase == "elimination":
            adjustedConcentration, massUnit, adjustedPrecision = adjustConcentrationFromUnit(totalConcentration, adjustedConcentration, precision, adjustedPrecision, massUnit)
            if pkInfo.dr_max:
                concentration_response = defaultDrResult(phase, delayedPhase, adjustedConcentration, adjustedPrecision, massUnit, maxMassUnit, drMaxConcentration)
            else:
                concentration_response = defaultDrResult(phase, delayedPhase, adjustedConcentration, adjustedPrecision, massUnit)
        elif massUnit != None and (phase in ["absorption", "distribution", "elimination"] and delayedPhase in ["absorption", "distribution", "lag"]):
            if pkInfo.dr_max:
                concentration_response = defaultDrResult(phase, delayedPhase, totalConcentration, precision, massUnit, maxMassUnit, drMaxConcentration)
            else:
                concentration_response = defaultDrResult(phase, delayedPhase, totalConcentration, precision, massUnit)
        else:
            if pkInfo.dr_max:
                concentration_response = defaultDrResult(phase, delayedPhase, totalConcentration, precision, max_concentration=drMaxConcentration)
            else:
                concentration_response = defaultDrResult(phase, delayedPhase, totalConcentration, precision)
        print("\x1b[2K%s" % concentration_response, end='\r', flush=True)
        if checkIfEliminated(totalConcentration, delayedPhase):
            timeSinceAdministration = timeSinceStart + drugInfo.lagtime if drugInfo.lagtime != None else float(timeSinceStart)
            completeScript(timeSinceAdministration, pkInfo.autocomplete)

