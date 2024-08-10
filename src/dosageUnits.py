__all__ = [
    "getDosePrecisionString",
    "unitToMgFraction",
    "adjustConcentrationForUnit",
]

def adjustConcentrationForUnit(doseValues: tuple, units: tuple, precisionValues: tuple) -> tuple:
    """
    :param doseValues: main dose and converted dose
    :type doseValues: tuple
    :param units: main mass unit and converted mass unit
    :type units: tuple
    :param precisions: main precision and converted precision
    :type precisions: tuple
    :returns: newDose, newUnit, newPrecision
    """
    mainDose, newDose = doseValues
    mainPrecision, newPrecision = precisionValues
    mainUnit, newUnit = units
    if mainUnit not in ["mg", "mcg", "g"]:
        return mainDose, mainUnit, mainPrecision
    if newPrecision >= 3 and int(newDose) == 0:
        if int(newDose) == 0 and newUnit != "mcg":
            newPrecision -= 3
            newUnit = "mg" if newUnit == "g" else "mcg"
    if mainPrecision - newPrecision != 0:
        newDose = int(mainDose * pow(10, mainPrecision + (mainPrecision - newPrecision))) / pow(10, mainPrecision)
    else:
        newDose = float(mainDose)
    if newPrecision == 0:
        newDose = int(newDose)
    return newDose, newUnit, newPrecision

def getDosePrecisionString(concentration: float, precision: int):
    if precision != 0:
        return str("{:."+str(precision)+"f}").format(concentration)
    return str(int(concentration))

def unitToMgFraction(unit: str) -> float:
    if unit in ["g", "gram", "grams"]:
        frac = 1e3
    elif unit in ["mcg", "ug", "microgram", "micrograms"]:
        frac = 1/1e3
    elif unit == None or unit in ["mg", "milligram", "milligrams"]:
        frac = 1
    return frac
