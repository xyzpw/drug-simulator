def adjustConcentrationFromUnit(conc: float, adjConc: float, prec: int, adjPrec: int, unit: str):
    if adjPrec >= 3 and int(adjConc) == 0:
        if int(adjConc) == 0 and unit != "mcg":
            adjPrec -= 3
            if unit == "g":
                unit = "mg"
            elif unit == "mg":
                unit = "mcg"
    if prec - adjPrec != 0:
        adjConc = int(conc * 10**(prec+(prec-adjPrec))) / 10**(prec)
    else:
        adjConc = conc
    if adjPrec == 0:
        adjConc = int(adjConc)
    return adjConc, unit, adjPrec

def concentrationFloatString(concentration: float, precision: int):
    if precision != 0:
        return str("{:."+str(precision)+"f}").format(concentration)
    return concentration

def unitToMgFraction(unit: str) -> float:
    if unit in ["g", "gram", "grams"]:
        frac = 1e3
    elif unit in ["mcg", "ug", "microgram", "micrograms"]:
        frac = 1/1e3
    elif unit == None or unit in ["mg", "milligram", "milligrams"]:
        frac = 1
    return frac
