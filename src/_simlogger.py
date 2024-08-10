
__all__ = [
    "SimulationInfoContainer",
]

class SimulationInfoContainer:
    """Stores information about the simulation."""
    def __init__(self, **kwargs):
        for k,v in kwargs.items():
            setattr(self, k, v)
