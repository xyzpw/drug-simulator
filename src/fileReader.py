import json
import pathlib
import re

__all__ = [
    "validateFileArgs",
    "readFile",
]

def readFile(location: str) -> dict:
    """Returns the file contents in dictionary format."""
    filenameRegexSearch = re.search(r"^(?!\.)(?P<name>[-.\w\d ]+?)(?:\.json)?$", location)
    filename = filenameRegexSearch.group("name") + ".json" if filenameRegexSearch else None
    if not filename:
        return
    with open(filename, "r") as f:
        fileContent = json.load(f)
    return fileContent

def validateFileArgs(location: str, usrArgs: dict) -> dict:
    """Changes command-line argument values to those in the file's contents."""
    fileContent = readFile(location)
    if not fileContent:
        return usrArgs

    updateUsrArgs = lambda key, value: usrArgs.update({key: value})
    checkShouldUpdate = lambda name: usrArgs.get(name) == None and fileContent.get(name) != None

    fileValueNames = [
        "dose", "t12", "t12a", "t12abs", "lagtime", "msg",
        "bioavailability", "dr", "irfrac", "minimum", "dr_max", "roa",
        "prodrug", "activeT12",
    ]

    for name in fileValueNames:
        _value = fileContent.get(name)
        if checkShouldUpdate(name):
            updateUsrArgs(name, _value)
        del name, _value
    return usrArgs
