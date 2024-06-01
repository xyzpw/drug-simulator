import json
import pathlib
import re

__all__ = [
    "readFile",
    "validateFileArgs",
]

def validateFile(location):
    if not bool(re.search(r"^[\w\s\-\_]*?(\.json)?$", str(location))):
        return Exception("illegal characters in file name")
    if not str(location).endswith(".json"): location += ".json"
    if not pathlib.Path(location).exists():
        return FileNotFoundError("file does not exist")
    return True

def readFile(location: str) -> dict:
    validateFileResults = validateFile(location)
    if validateFileResults != True:
        raise validateFileResults
    with open(location, "r") as f:
        fileContents = f.read()
    fileContents: dict = json.loads(fileContents)
    return fileContents

def validateMethods(usrArgs: dict, usrMethods: list):
    methods = ["probability", "linear", "linearabs", "dr_max"]
    for method in methods:
        if method in usrMethods:
            usrArgs[method] = True
    return usrArgs

def validateFileArgs(location: str, args: dict) -> dict:
    if not str(location).endswith(".json"): location += ".json"
    phContents = readFile(location)
    fileArgArray = [
        "dose",
        "tmax",
        "t12",
        "t12a",
        "t12abs",
        "lagtime",
        "msg",
        "bioavailability",
        "dist_time",
        "dr",
        "irfrac",
        "minimum",
        "methods",
    ]
    for i in fileArgArray:
        if i == "methods":
            if phContents.get(i) != None:
                args = validateMethods(args, phContents.get(i))
            continue
        if not bool(args.get(i)) and bool(phContents.get(i)):
            args[i] = phContents.get(i)
            if i == "bioavailability":
                args[i] = float(args[i])
    return args
