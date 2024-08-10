import math
import re
from ._simlogger import *

__all__ = [
    "getDoseWithPrecision",
    "completeScript",
    "checkIfEliminated",
    "computeOralDrugContent",
    "computeDrOralDrugContent",
    "computeOralRoutePhase",
    "computeLinearAbsorbed",
    "computeRetentionProbability",
    "computeIvDrugContent",
    "computeAbsorbedDose",
    "computeIvAmountExcreted",
    "computeOralProdrugConcentrations",
    "computeOralAmountEliminated",
]

def computeIvDrugContent(initialDose: float, elapsed: float, halflife: float):
    return pow(1/2, elapsed / halflife) * initialDose

def computeAbsorbedDose(initialDose: float, elapsed: float, halflifeAbs) -> float:
    return (1 - pow(1/2, elapsed / halflifeAbs)) * initialDose

def computeRetentionProbability(elapsed: float, halflife: float) -> float:
    return pow(1/2, elapsed / halflife)

def computeLinearAbsorbed(dose: float, tmax: float, elapsed: float) -> float:
    return elapsed / tmax * dose

def computeOralDrugContent(dose: float, bioavailability: float, halflives: tuple, timeElapsed: float) -> float:
    """
    :param halflives: absorption half-life and elimination half-life
    :type halflives: tuple
    """
    ka = math.log(2) / halflives[0]
    ke = math.log(2) / halflives[1]
    if ka == ke: # if `ka` and `ke` are equivalent, a different formula must be used
        return bioavailability * dose * ka * timeElapsed * math.e**(-ka*timeElapsed)
    numerator = bioavailability * dose * ka
    denominator = ka - ke
    multiplier = math.e**(-ke * timeElapsed) - math.e**(-ka * timeElapsed)
    return (numerator / denominator) * multiplier

def computeDrOralDrugContent(doses: tuple[float], bioavailability: float, halflives: tuple, timesElapsed: tuple[float]) -> float:
    """
    :param doses: irDose and drDose
    :type doses: tuple
    :param halflives:
    :type halflives: tuple
    :param timesElapsed: time since ir and dr appearance
    :type timesElapsed: tuple
    :returns: irDose, drDose
    """
    irRemaining = computeOralDrugContent(doses[0], bioavailability, halflives, timesElapsed[0])
    drRemaining = computeOralDrugContent(doses[1], bioavailability, halflives, timesElapsed[1]) if timesElapsed[1] > 0 else 0
    return irRemaining, drRemaining

def computeOralRoutePhase(halflives: tuple, timeElapsed: float) -> str:
    if timeElapsed < 0:
        return "lag"
    ka = math.log(2) / halflives[0]
    ke = math.log(2) / halflives[1]
    # `ka` cannot be equivalent to `ke`; a different formula must be used
    tmax = math.log(ka / ke) / (ka - ke) if ka != ke else 1/ka
    return "elimination" if timeElapsed > tmax else "absorption"

def computeIvAmountExcreted(concentration, unchangedFraction: float, halflife: float, elapsed: float) -> tuple:
    """
    Calculates the amount of the drug has been excreted unchanged

    :returns: remaining dose, unchanged dose excreted
    :rtype: tuple
    """
    kel = math.log(2) / halflife # constant elimination rate (usually known as 'ke')
    ke = kel * unchangedFraction # constant excretion rate
    remainingDose = concentration * math.exp(-kel * elapsed)
    unchangedExcreted = ke * concentration / kel * (1 - math.exp(-kel * elapsed))
    return remainingDose, unchangedExcreted

def computeOralAmountEliminated(concentration: float, bioavailability: float, halflives: tuple, elapsed: float) -> float:
    """
    :param halflives: absorption and elimination half-life, respectively
    :type halflives: tuple
    """
    ka = math.log(2) / halflives[0]
    ke = math.log(2) / halflives[1]
    concentrationRemaining = computeOralDrugContent(concentration, bioavailability, halflives, elapsed)
    amountAbsorbed = concentration * (1 - math.exp(-ka * elapsed))
    return amountAbsorbed - concentrationRemaining

def computeOralProdrugConcentrations(initialDose: float, halflives: tuple, fracs: tuple, elapsed: float) -> float:
    """
    :param halflives: absorption and elimination of prodrug and elimination half-life of active drug, respectively
    :type halflives: tuple
    :param fracs: bioavailability of prodrug and fraction of prodrug which converts into active drug, respectively
    :type fracs: tuple
    """
    activeDrugKe = math.log(2) / halflives[2]
    prodrugDose = computeOralDrugContent(initialDose, fracs[0], (halflives[0], halflives[1]), elapsed)
    prodrugEliminated = computeOralAmountEliminated(initialDose, fracs[0], (halflives[0], halflives[1]), elapsed)
    activeDrugDose = prodrugEliminated * fracs[1]
    activeDrugDose *= math.exp(-activeDrugKe * elapsed)
    return prodrugDose, activeDrugDose

def getDoseWithPrecision(currConcentration: float, currPrecision: int) -> float | int:
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

def completeScript(elapsed: bool):
    print('\n')
    completionMessage = getCompletionMessage(elapsed)
    input("%s. Press enter to exit" % completionMessage)
    raise SystemExit(0)

def checkIfEliminated(concentration, phase=None, minimum_concentration=None):
    if minimum_concentration == None: minimum_concentration = 0
    if concentration <= minimum_concentration and phase in ["elimination", None, "distribution"]:
        return True
