from src._dosageUnits import concentrationFloatString

def defaultResult(phase: str, concentration: float, prec: int = 0, mass_unit: str = None) -> str:
    concentrationStr = concentrationFloatString(concentration, prec)
    result = f"concentration ({phase}): {concentrationStr}"
    if mass_unit != None:
        result += f" {mass_unit}"
    return result

def defaultDrResult(phase: str, delayedPhase: str, concentration: float, prec: int = 0, mass_unit: str = None, max_massUnit: str = None, max_concentration: float = False) -> str:
    concentration = concentrationFloatString(concentration, prec)
    maxConcentrationStr = concentrationFloatString(max_concentration, prec)
    result = f"concentration ({phase}[DR: {delayedPhase}]): {concentration}"
    if mass_unit != None:
        result += f" {mass_unit}"
    if max_concentration != False:
        if max_massUnit != None:
            result += f" (max. achieved: {maxConcentrationStr} {max_massUnit})"
        else:
            result += f" (max. achieved: {maxConcentrationStr})"
    return result

def probabilityResult(probability: float, prec: int, hasTmaxed: bool) -> str:
    fixedProbability = concentrationFloatString(probability, prec) if prec > 0 else int(probability)
    if hasTmaxed:
        return "molecular retention probability: %s" % str(fixedProbability) + "%"
    return "amount absorbed: %s" % str(fixedProbability) + "%"

def probabilityDrResult(irProbability: float, drProbability: float, prec: int,
                        irHasTmaxed: bool, drHasTmaxed: bool) -> tuple[str]:
    fixedIrProbability = concentrationFloatString(irProbability, prec) if prec >= 0 else int(irProbability)
    fixedDrProbability = concentrationFloatString(drProbability, prec) if prec >= 0 else int(drProbability)
    getTmaxedString = lambda prob, release: "molecular retention probability (%s): %s" % (release, str(prob) + "%")
    getNotTmaxedString = lambda prob, release: "amount absorbed (%s): %s" % (release, str(prob) + "%")
    irResult = getTmaxedString(fixedIrProbability, "IR") if irHasTmaxed else getNotTmaxedString(fixedIrProbability, "IR")
    drResult = getTmaxedString(fixedDrProbability, "DR") if drHasTmaxed else getNotTmaxedString(fixedDrProbability, "DR")
    return irResult, drResult
