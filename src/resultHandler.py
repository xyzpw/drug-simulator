from src.dosageUnits import getDosePrecisionString

def getDefaultResult(phase: str, concentration: float, prec: int = 0, mass_unit: str = None) -> str:
    concentrationStr = getDosePrecisionString(concentration, prec)
    result = f"drug content ({phase}): {concentrationStr}"
    if mass_unit != None:
        result += f" {mass_unit}"
    return result

def getDefaultDrResult(remaining: float, peakReached: float, precisions: tuple, massUnits: tuple, phases: tuple) -> str:
    """
    :param remaining: total dose remaining
    :param peakReached: highest dose achieved (can be set to `None`)
    :type peakReached: float
    :param precisions: dose precision and peak achieved precision
    :type precisions: tuple
    :param massUnits: ir mass unit and max achieved mass unit (default 0)
    :type massUnits: tuple, bool
    :param phases: ir phase and dr phase
    :type phases: tuple
    """
    irPhase, drPhase = phases
    doseStr = getDosePrecisionString(remaining, precisions[0] if precisions[0] != None else 0)
    if massUnits[0] != None: doseStr += " %s" % massUnits[0]
    result = "drug content (%s[DR: %s]): %s" % (irPhase, drPhase, doseStr)
    if peakReached != None:
        maxDoseStr = getDosePrecisionString(peakReached, precisions[1] if precisions[1] != None else 0)
        if massUnits[1] != None: maxDoseStr += " %s" % massUnits[1]
        result += " (max. achieved: %s)" % maxDoseStr
    return result

def getProbabilityResult(probability: float, prec: int, hasTmaxed: bool) -> str:
    probability *= 100 # convert to percent
    fixedProbability = getDosePrecisionString(probability, prec) if prec > 0 else int(probability)
    if hasTmaxed:
        return "molecular retention probability: %s" % str(fixedProbability) + "%"
    return "amount absorbed: %s" % str(fixedProbability) + "%"

def getProbabilityDrResult(probabilities: tuple, precisions: tuple, hasTmaxed: tuple) -> tuple[str]:
    """
    :param probabilities: ir probability, dr probability
    :type probabilities: tuple
    :param precisions: ir precision, dr precision
    :type precisions: tuple
    :param hasTmaxed: value to determine if tmax has been reached, ir and dr
    :type hasTmaxed: tuple
    """
    probabilities = probabilities[0]*100, probabilities[1]*100 # convert to percent
    irProbabilityStr = getDosePrecisionString(probabilities[0], precisions[0])
    drProbabilityStr = getDosePrecisionString(probabilities[1], precisions[1])
    getTmaxedStr = lambda p, release: "molecular retention probability (%s): %s" % (release, str(p) + "%")
    getNotTmaxedStr = lambda p, release: "amount absorbed (%s): %s" % (release, str(p) + "%")
    irResult = getTmaxedStr(irProbabilityStr, "IR") if hasTmaxed[0] else getNotTmaxedStr(irProbabilityStr, "IR")
    drResult = getTmaxedStr(drProbabilityStr, "DR") if hasTmaxed[1] else getNotTmaxedStr(drProbabilityStr, "DR")
    return irResult, drResult

def getExcretionResult(excretedAmount: tuple, resultPrecision: int) -> str:
    """
    :param excretedAmount: dose and mass unit
    :type excretedAmount: tuple
    """
    excretedDose, excretedMassUnit = excretedAmount
    excretedStr = getDosePrecisionString(excretedDose, resultPrecision)
    if excretedMassUnit != None:
        excretedStr += " %s" % excretedMassUnit
    return "unchanged dose excreted: %s" % excretedStr

def getOralProdrugResult(doses: tuple, dosePrecision: int, massUnit: str, prodrugIsEliminated: bool) -> str:
    """
    :param doses: prodrug and active drug, respectively
    :type doses: tuple
    """
    doseStr = getDosePrecisionString(doses[0], dosePrecision)
    activeDoseStr = getDosePrecisionString(doses[1], dosePrecision)
    if massUnit != None:
        doseStr += " %s" % massUnit
        activeDoseStr += " %s" % massUnit
    result = "active drug content: %s" % activeDoseStr
    if not prodrugIsEliminated:
        result += " (prodrug %s)" % doseStr
    return result
