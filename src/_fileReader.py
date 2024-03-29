import json
import pathlib

__all__ = [
    "readFile",
    "validateFileArgs",
]

def validateFile(location):
    if not str(location).endswith(".json"): location += ".json"
    if not pathlib.Path(location).exists():
        return FileNotFoundError("file does not exist")
    return True

def readFile(location: str) -> dict:
    if not str(location).endswith(".json"): location += ".json"
    validateFileResults = validateFile(location)
    if validateFileResults != True:
        raise validateFileResults
    with open(location, "r") as f:
        fileContents = f.read()
    fileContents: dict = json.loads(fileContents)
    return fileContents

def validateFileArgs(location: str, args: dict) -> dict:
    if not str(location).endswith(".json"): location += ".json"
    phContents = readFile(location)
    fileArgList = ["lagtime", "msg", "dr", "bioavailability"]
    for i in fileArgList:
        if bool(phContents.get(i)) and not bool(args.get(i)):
            args[i] = phContents.get(i)
    return args
