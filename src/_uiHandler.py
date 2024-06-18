import re
from ._timeConversions import fixTimeUI

__all__ = [
    "fixDose",
    "fixTmax",
    "fixT12abs",
    "fixT12",
    "fixDr",
    "doseWithBioavailability",
    "getValueFromFraction",
]

def fixDose(dose: str|float, isProbability=False) -> tuple:
    massunit = None
    if isProbability:
        return float(1), massunit
    if isinstance(dose, str):
        dose = dose.replace(",", "")
        if "/" in dose:
            doseFractionValue = getValueFromFraction(dose)
            dose = re.sub(r"^((?:\d*\.)?\d+\s*/\s*(?:\d*\.)?\d+)", f"{doseFractionValue}", dose)
    massUnitSearch = re.search(r"^(?P<dose>(?:\d+?\.)?\d+)\s?(?P<unit>mg|milligrams?|ug|mcg|micrograms?|g|grams?)$", str(dose))
    if bool(massUnitSearch):
        dose = float(massUnitSearch.group("dose"))
        massunit = massUnitSearch.group("unit")
        match massunit:
            case "mg" | "milligram" | "milligrams":
                massunit = "mg"
            case "ug" | "mcg" | "micrograms" | "microgram":
                massunit = "mcg"
            case "g" | "gram" | "grams":
                massunit = 'g'
            case _:
                raise SystemExit("invalid mass unit for dosage")
    return fixTimeUI(str(dose)), massunit

def fixTmax(tmax: float|str, peaked=False) -> float:
    if peaked or tmax in ["now", "0", ""]:
        return float(0)
    return fixTimeUI(str(tmax))

def fixT12abs(t12abs: str|float) -> float:
    return fixTimeUI(str(t12abs))

def fixT12(t12: str|float) -> float:
    return fixTimeUI(str(t12))

def doseWithBioavailability(bioavailability: float, initialDose: float|int) -> float:
    return initialDose * bioavailability

def fixDr(irFrac: float, drLagTime: float|int) -> tuple:
    drLagTime = fixTimeUI(drLagTime)
    if irFrac in [None, '']: irFrac = 0.5
    irFrac = fixTimeUI(irFrac)
    if 1 < irFrac <= 0:
        raise ValueError("instant release must greater than 0 and less than 1")
    return irFrac, drLagTime

def getValueFromFraction(userValue: str):
    fractionReMatch = re.search(r"^(?P<num>(?:\d*\.)?\d+)\s*?/\s*?(?P<den>(?:\d*\.)?\d+)", userValue)
    numerator, denominator = float(fractionReMatch.group("num")), float(fractionReMatch.group("den"))
    return numerator / denominator
