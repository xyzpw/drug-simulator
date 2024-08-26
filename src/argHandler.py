import argparse
import re
from src._argInfo import *

__all__ = [
    "getSimulationMethod",
    "getTimeFormat",
    "validateArgs",
    "parseAndReturnArgs",
]

def _displayManual():
    manual = """Drug simulator manual.

Route of Administration
    iv
    iv-excretion
    oral
    oral-dr
    oral-excretion
    oral-prodrug (results are estimations)

    Custom Options
        NOTE: custom roa will affect accuracy

        custom
        custom-dr
        custom-probability
        custom-probability-dr

        Custom options allow some additional options to be used, but it will affect results accuracy.


Time Units
    Units include: second(s), minute(s), hour(s), and day(s).
    If no units are included, seconds will be used.
    The first word of the unit can be used, e.g. m for minute(s).
    Spaces can be included between the dose and the unit.

Dosage Units
    Units include: mg, milligram(s), ug, mcg, microgram(s), g, gram(s)
    Spaces can be included between the dose and the unit.

Time Formats
    Colons between minutes are optional, e.g. 2100 => 21:00
    Entering a date: 202401100100 is interpreted as 2024-01-10 at 0100 hours
    Optional: "20240110 0100"
"""
    try:
        import pydoc
        pydoc.pager(manual)
    except:
        print(manual)

def getTimeFormat(usrFormat: str):
    tFormat = r"%H%M (%Y-%m-%d)"
    if usrFormat == "12":
        tFormat = r"%I:%M:%S %p (%m/%d/%Y)"
    elif usrFormat == "24":
        tFormat = r"%H:%M:%S (%Y-%m-%d)"
    return tFormat

def addCountToMsg(msg: str, count: str):
    isInt = bool(re.search(r"^\d+$", count))
    if isInt: count = int(count)
    return "%sx %s" % (count, msg)

def _exitWithError(error):
    raise SystemExit(error)

def validateArgs(argsDict: dict):
    checkArgHasValue = lambda argName: argsDict.get(argName) != None
    checkArgIsTrue = lambda argName: argsDict.get(argName) == True
    checkArgIsNoneOrFalse = lambda name: argsDict.get(name) in [None, False]

    if checkArgIsTrue("man"):
        _displayManual()
        raise SystemExit(0)
    if not False in [checkArgHasValue(i) for i in ["msg", "count"]]:
        argsDict["msg"] = addCountToMsg(argsDict.get("msg"), argsDict.get("count"))

    # arguments that can not be used together (only one at a time)
    argsWithConflicts = [
        ["date", "time", "elapsed"],
    ]

    # each key represents an argument, if that argument is used, another argument must also be used with the value in the tuple index 1...
        # e.g. {"argument": ("must also use this argument", "with this value", "or this value...")}
    argsMustAccompanyWithValues = {
        "prodrug": ("roa", "oral-prodrug"),
        "linearabs": ("roa", "custom", "custom-dr", "custom-probability", "custom-probability-dr")
    }
    for i in ["dist_time", "t12a"]:
        argsMustAccompanyWithValues.update({
            i: ("roa", "custom", "custom-dr")
        })

    # Check for conflicts in arguments
    for conflictList in argsWithConflicts:
        if [checkArgHasValue(i) for i in conflictList].count(True) > 1:
            conflicts = [i for i in conflictList if checkArgHasValue(i)]
            _exitWithError("conflicts detected: %s" % (", ".join(conflicts)))

    # Check if required accompanied arguments are proper values
    for argName, requiredArgContent in argsMustAccompanyWithValues.items():
        if not checkArgIsNoneOrFalse(argName):
            requiredArgName = requiredArgContent[0]
            validArgValues = requiredArgContent[1:]
            if not argsDict.get(requiredArgName) in validArgValues:
                _exitWithError(
                    "argument '%s' must be equal to one of the following values: %s" % (
                        requiredArgName, ", ".join(validArgValues))
                )

    # Check for invalid `dr` argument usage
    if checkArgHasValue("dr"):
        if not argsDict.get("roa") in ["oral-dr", "custom-dr", "custom-probability-dr"]:
            raise SystemExit("invalid route of administration")

def parseAndReturnArgs() -> dict:
    """Creates and returns arguments via `argparse` module.
    :rtype: dictionary
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        description="A program which simulates the concentration of drugs in real time.",
    )
    parser.add_argument("--help", "-h", help="displays this menu and exits", action="help")
    # Add arguments
    for arg, kwargs in parserKwarg.items():
        _prefix = "--" if len(arg) > 1 else "-"
        parser.add_argument(f"{_prefix}{arg}", **kwargs)
    return vars(parser.parse_args())

def getSimulationMethod(usrArgs: dict):
    return usrArgs.get("roa") if usrArgs.get("roa") else "iv"

#lolayylmao:DD