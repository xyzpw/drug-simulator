from src._simulationImports import *

__all__ = [
    "getSimulationFunction",
    "getAppearanceEpoch",
]

def getSimulationFunction(method: str):
    """Returns the function to be used which will initiate the simulation."""
    options = {
        "iv": simulateIvBolus,
        "iv-excretion": simulateIvBolusExcretion,
        "oral": simulateOralAdministration,
        "oral-dr": simulateDrOralAdministration,
        "oral-excretion": simulateOralAdministrationExcretion,
        "oral-prodrug": simulateProdrugOralAdministration,
        "custom": simulateCustomAdministration,
        "custom-dr": simulateCustomDrAdministration,
        "custom-probability": simulateCustomDecayProbability,
        "custom-probability-dr": simulateCustomDrDecayProbability,
    }
    if not method in list(options):
        raise SystemExit("invalid route of administration")
    return options.get(method)

def getAppearanceEpoch(simInfo: object):
    if not hasattr(simInfo, "lagtime"):
        return simInfo.doseEpoch
    appearanceEpoch = simInfo.doseEpoch + simInfo.lagtime
    return appearanceEpoch
