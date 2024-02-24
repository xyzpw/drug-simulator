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
