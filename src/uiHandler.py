import re
from .timeConversions import fixTimeUi
from datetime import datetime
from .dosageUnits import unitToMgFraction

__all__ = [
    "fixDose",
    "fixTmax",
    "fixT12abs",
    "fixT12",
    "fixDr",
    "doseWithBioavailability",
    "getValueFromFraction",
    "getUiValue",
    "getSimulationMessage",
    "detectAndFixValue",
    "getValueFromMultiplier",
    "fixCountValue",
    "getValueFromMathInput",
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
        elif "*" in dose:
            doseMultiplierValue = getValueFromMultiplier(dose)
            dose = re.sub(r"((?:\d*\.)?\d+\s*?\*\s*?(?:\d*\.)?\d+)", f"{doseMultiplierValue}", dose)
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
    return fixTimeUi(str(dose)), massunit

def fixCountValue(value: int | float | str) -> float:
    isInteger = re.search(r"^\d+?$", value)
    isFloat = re.search(r"^\d+?\.\d+?$", value)
    isMultiplier = "*" in str(value)
    isFraction = "/" in str(value)
    if isInteger:
        return int(value)
    elif isFloat:
        return float(value)
    elif isMultiplier:
        return getValueFromMultiplier(value)
    elif isFraction:
        return getValueFromFraction(value)

def fixTmax(tmax: float|str, peaked=False) -> float:
    if peaked or tmax in ["now", "0", ""]:
        return float(0)
    return fixTimeUi(str(tmax))

def fixT12abs(t12abs: str|float) -> float:
    return fixTimeUi(str(t12abs))

def fixT12(t12: str|float) -> float:
    return fixTimeUi(str(t12))

def doseWithBioavailability(bioavailability: float, initialDose: float|int) -> float:
    return initialDose * bioavailability

def fixDr(irFrac: float, drLagTime: float|int) -> tuple:
    drLagTime = fixTimeUi(drLagTime)
    if irFrac in [None, '']: irFrac = 0.5
    irFrac = fixTimeUi(irFrac)
    if 1 < irFrac <= 0:
        raise ValueError("instant release must greater than 0 and less than 1")
    return irFrac, drLagTime

def getValueFromFraction(userValue: str):
    fractionReMatch = re.search(r"^(?P<num>(?:\d*\.)?\d+)\s*?/\s*?(?P<den>(?:\d*\.)?\d+)", userValue)
    numerator, denominator = float(fractionReMatch.group("num")), float(fractionReMatch.group("den"))
    return numerator / denominator

def getValueFromMultiplier(userValue: str):
    multiplyNumberRegex = re.search(r"^(?P<multiplier>(?:\d*\.)?\d+)\s*?\*\s*?(?P<number>(?:\d*\.)?\d+)", userValue)
    number = float(multiplyNumberRegex.group("multiplier")) * float(multiplyNumberRegex.group("number"))
    return number

def getValueFromMathInput(value: str):
    if "/" in value:
        return getValueFromFraction(value)
    elif "*" in value:
        return getValueFromMultiplier(value)

def getUiValue(usrArgs: dict, desiredValueArg: str, altPromptText: str):
    """Gets value from arg if it exists, otherwise prompts the user for the value.
    No prompt will occur if `altPromptText` is set to `None`."""
    return usrArgs.get(desiredValueArg) if usrArgs.get(desiredValueArg) != None else (input(altPromptText) if altPromptText != None else None)

def getSimulationMessage(userMsg: str, displayTimeEpoch: float, displayTimeFormat: str) -> str:
    """Displays the message prior to simulation commencement."""
    timeLabel = "time at administration"
    datetimeString = datetime.fromtimestamp(displayTimeEpoch).strftime(displayTimeFormat)
    finalMessage = "{}{}: {}\n".format(
        "\n%s\n\n" % userMsg if userMsg != None else "\n",
        timeLabel,
        datetimeString,
    );return finalMessage

def detectAndFixValue(valueName: str, value: str):
    match valueName:
        case "dose":
            return fixDose(value)
        case "minimum":
            value = fixDose(value)
            return unitToMgFraction(value[1]) * value[0]
        case "tmax":
            return fixTmax(value)
        case "t12" | "t12a" | "t12abs" | "dist_time" | "dr" | "lagtime" | "activeT12":
            return fixTimeUi(value)
        case "bioavailability" | "irfrac" | "excretionUnchanged" | "prodrug":
            if valueName == "irfrac" and value == "":
                return 0.5
            if "/" in str(value) or "*" in str(value):
                value = getValueFromMathInput(value)
            if not 1 >= float(value) >= 0:
                raise ValueError("'%s' must be greater than 0 and no greater than 1" % valueName)
            return float(value)
        case "precision":
            return int(value)
