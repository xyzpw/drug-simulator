
def getT12(phase: str, t12, t12abs, t12a) -> float:
    match phase:
        case "absorption":
            return t12abs
        case "distribution":
            return t12a
        case "elimination":
            return t12
