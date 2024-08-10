from .uiHandler import *

__all__ = [
    "getAllRequiredValues",
]

def getDefaultRequiredValuesForMethod(usrMethod: str) -> dict:
    requiredValues = {}
    updateValues = requiredValues.update
    """
    `requiredValues` usage:
        Key is the attribute name to the class which contains the simulation info
        Value is the text that will be prompted on screen asking for user input (None for no input)
    """
    match usrMethod:
        case "iv":
            updateValues({
                "dose": "dose",
                "t12": "half-life",
            })
        case "iv-excretion":
            updateValues({
                "dose": "dose",
                "t12": "half-life",
                "excretionUnchanged": "fraction of dose excreted as unchanged",
            })
        case "oral":
            updateValues({
                "dose": "dose",
                "bioavailability": "bioavailability",
                "t12abs": "absorption half-life",
                "t12": "half-life",
            })
        case "oral-dr":
            updateValues({
                "dose": "dose",
                "bioavailability": "bioavailability",
                "t12abs": "absorption half-life",
                "t12": "half-life",
                "dr": "time until delayed dose",
                "irfrac": "instant release dose fraction (def. 0.5)",
            })
        case "oral-excretion":
            updateValues({
                "dose": "dose",
                "bioavailability": "bioavailability",
                "excretionUnchanged": "fraction of dose excreted as unchanged",
                "t12abs": "absorption half-life",
                "t12": "half-life",
            })
        case "oral-prodrug":
            updateValues({
                "dose": "dose",
                "bioavailability": "prodrug bioavailability",
                "t12abs": "prodrug absorption half-life",
                "t12": "prodrug half-life",
                "prodrug": "fraction of prodrug converts into active",
                "activeT12": "active drug half-life",
            })
        case "custom":
            updateValues({
                "dose": "dose",
                "t12abs": "absorption half-life",
                "tmax": "tmax",
                "t12": "half-life",
            })
        case "custom-dr":
            updateValues({
                "dose": "dose",
                "t12abs": "absorption half-life",
                "tmax": "tmax",
                "t12": "half-life",
                "dr": "time until delayed dose",
                "irfrac": "instant release dose fraction (def. 0.5)",
            })
        case "custom-probability":
            updateValues({
                "t12abs": "absorption half-life",
                "tmax": "tmax",
                "t12": "half-life",
            })
        case "custom-probability-dr":
            updateValues({
                "t12abs": "absorption half-life",
                "tmax": "tmax",
                "t12": "half-life",
                "dr": "time until delayed dose",
            })
    # Adding colon to end of values because they will be prompted
    for i in list(requiredValues):
        if requiredValues[i] != None:
            requiredValues[i] = "%s: " % requiredValues[i]
    return requiredValues

def updateRequiredValuesForArgs(usrArgs: dict, requiredValues: dict) -> dict:
    addValue = lambda key, value: requiredValues.update({key: value})
    removeValue = lambda key: requiredValues.pop(key)
    checkUsrArgHasValue = lambda name: usrArgs.get(name) != None
    checkUsrArgIsTrue = lambda name: usrArgs.get(name) == True
    checkUsrArgIsNoneOrFalse = lambda name: usrArgs.get(name) in [None, False]

    if checkUsrArgHasValue("lagtime"):
        addValue("lagtime", None)

    if checkUsrArgIsTrue("dr_max"):
        addValue("dr_max", None)

    if checkUsrArgIsTrue("linearabs"):
        removeValue("t12abs")
        addValue("linearabs", None)

    if True in [not checkUsrArgIsNoneOrFalse(i) for i in ["dist_time", "t12a", "biphasic"]]:
        requiredValues.update({
            "dist_time": "distribution time",
            "t12a": "distribution half-life",
        })

    if checkUsrArgHasValue("precision"):
        addValue("precision", None)

    for i in ["time", "elapsed", "date"]:
        if checkUsrArgHasValue(i):
            addValue(i, None)

    if checkUsrArgHasValue("minimum"):
        addValue("minimum", None)

    for i in list(requiredValues):
        if requiredValues[i] != None:
            if not str(requiredValues[i]).endswith(": "):
                requiredValues[i] = "%s: " % requiredValues[i]
    return requiredValues

def getAllRequiredValues(usrArgs: dict, method: str) -> dict:
    requiredValues = getDefaultRequiredValuesForMethod(method)
    requiredValues = updateRequiredValuesForArgs(usrArgs, requiredValues)
    return requiredValues
