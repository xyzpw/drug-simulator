
__all__ = [
    "SimulationInfoContainer",
    "InfoFetcher",
]

class SimulationInfoContainer:
    """Stores information about the simulation."""
    def __init__(self, **kwargs):
        for k,v in kwargs.items():
            setattr(self, k, v)

class InfoFetcher:
    def __init__(self, drugInfo, simInfo):
        self.drugInfo = drugInfo
        self.simInfo = simInfo
    def getMainValues(self):
        """:returns: dose, massUnit, precision, isBiphasic"""
        return self.drugInfo.dose, self.drugInfo.massUnit, self.simInfo.precision, self.drugInfo.isBiphasic
    def getPeakAndPhaseValues(self):
        ":returns: tmax, hasTmaxed, phase, timeSinceTmax, tmaxedEpoch"
        hasTmaxed = True if self.simInfo.startAtCmax else False
        phase = "absorption" if not hasTmaxed else "elimination"
        return self.drugInfo.tmax, hasTmaxed, phase, None, None
    def getDrPhaseValues(self, startingEpoch):
        """:returns: delayedPhase, delayedHasTmaxed, delayedReleaseStarted"""
        if startingEpoch < (self.drugInfo.drLagtime + startingEpoch):
            delayedPhase = "lag"
            delayedHasTmaxed = False
            delayedReleaseStarted = False
        elif startingEpoch < (self.drugInfo.drLagtime + startingEpoch + self.drugInfo.tmax):
            delayedPhase = "absorption"
            delayedHasTmaxed = False
            delayedReleaseStarted = True
        elif startingEpoch >= (self.drugInfo.drLagtime + startingEpoch + self.drugInfo.tmax):
            delayedPhase = "elimination"
            delayedHasTmaxed = True
            delayedReleaseStarted = True
        return delayedPhase, delayedHasTmaxed, delayedReleaseStarted, self.drugInfo.drLagtime
