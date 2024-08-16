#!/usr/bin/env python3

from time import time as getCurrentEpoch
from src.timeConversions import *
from src.argHandler import *
from src.fileReader import *
from src.promptAuth import *
from src._simlogger import *
from src.dosageUnits import *
from src.uiHandler import *
from src.simulationDetector import *
from simulations.lagtimeCountdown import startLagtimeCountdown

args = parseAndReturnArgs()

drugFile = args.get("file")
if drugFile != None:
    args = validateFileArgs(drugFile, args)

validateArgs(args)

simulationInfo = SimulationInfoContainer(dose=1.0) # contains information required to run the simulation

simulationMethod = getSimulationMethod(args) # determines which simulation should be used

requiredValues = getAllRequiredValues(args, simulationMethod) # required values to simulate the method being used

try:
    # Prompts for required values to run the simulation (user input)
    for k, v in requiredValues.items():
        uiValue = getUiValue(args, k, v)
        setattr(simulationInfo, k, detectAndFixValue(k, uiValue))

    # Adjust dose if `count` argument is used
    if args.get("count"):
        simulationInfo.dose = simulationInfo.dose[0] * fixCountValue(args.get("count")), simulationInfo.dose[1]

    # Set each of these values to `0` if they are not used
    for i in ["precision", "minimum"]:
        if not hasattr(simulationInfo, i):
            setattr(simulationInfo, i, 0)
except (KeyboardInterrupt, EOFError):
    raise SystemExit(0)

# Setting epoch values
setattr(simulationInfo, "doseEpoch", getStartingEpoch(args))
setattr(simulationInfo, "appearanceEpoch", getAppearanceEpoch(simulationInfo))

commencementMessage = getSimulationMessage(
    args.get("msg"), simulationInfo.doseEpoch,
    getTimeFormat(args.get("time_format"))
)

isLag = hasattr(simulationInfo, "lagtime") and getCurrentEpoch() < simulationInfo.appearanceEpoch

initiateSimulation = getSimulationFunction(simulationMethod)

try:
    print(commencementMessage)
    if isLag:
        startLagtimeCountdown(simulationInfo.appearanceEpoch)
    initiateSimulation(simulationInfo)
except KeyboardInterrupt:
    raise SystemExit(0)
