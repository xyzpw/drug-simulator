def defaultResult(phase: str, concentration: float, mass_unit: str = None) -> str:
    result = f"concentration ({phase}): {concentration}"
    if mass_unit != None:
        result += f" {mass_unit}"
    return result

def defaultDrResult(phase: str, delayedPhase: str, concentration: float, mass_unit: str = None, max_massUnit: str = None, max_concentration: float = False) -> str:
    result = f"concentration ({phase}[DR: {delayedPhase}]): {concentration}"
    if mass_unit != None:
        result += f" {mass_unit}"
    if max_concentration != False:
        if max_massUnit != None:
            result += f" (max. achieved: {max_concentration} {max_massUnit})"
        else:
            result += f" (max. achieved: {max_concentration})"
    return result
