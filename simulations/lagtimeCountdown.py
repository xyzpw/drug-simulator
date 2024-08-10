from time import (
    time as getCurrentEpoch,
    sleep,
)

__all__ = [
    "startLagtimeCountdown",
]

updateInterval = 1/20

def startLagtimeCountdown(endEpoch: float):
    while True:
        timeUntilComplete = endEpoch - getCurrentEpoch()
        if timeUntilComplete <= 0:
            return
        minutesDigit = timeUntilComplete // 60
        secondsDigit = int(timeUntilComplete - minutesDigit * 60)
        if minutesDigit >= 1:
            timerOutput = (
                "%d minutes and %d seconds" % (minutesDigit, secondsDigit)
            ).replace(
                "minutes", "minute" if minutesDigit == 1 else "minutes"
            ).replace(
                "seconds", "second" if secondsDigit == 1 else "seconds"
            )
        else:
            timerOutput = (
                "%d seconds" % secondsDigit
            ).replace("seconds", "second" if secondsDigit == 1 else "seconds")
        print("\r\x1b[2Klagtime: %s" % timerOutput, end='', flush=True)
        sleep(updateInterval)
