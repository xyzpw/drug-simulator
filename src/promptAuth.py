from ._uiHandler import *

__all__ = [
    "authDosePrompt",
    "authT12absPrompt",
    "authDistributionPrompt",
    "authT12aPrompt",
    "authTmaxPrompt",
]

def authDosePrompt(isProbability: bool):
    if not isProbability:
        return True

def authT12absPrompt(isCmax: bool, isLinearabs: bool):
    if not isCmax and not isLinearabs:
        return True

def authDistributionPrompt(args: dict) -> bool:
    if args.get("dist_time") == None and args.get("t12a") != None:
        return True
    return args.get("biphasic")

def authT12aPrompt(args: dict):
    if args.get("t12a") == None and args.get("dist_time") != None:
        return True
    return args.get("biphasic")

def authTmaxPrompt(args: dict):
    if not args.get("tmaxed") or args.get("tmax") != None:
        return True


