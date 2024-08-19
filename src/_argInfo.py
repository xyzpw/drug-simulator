__all__ = [
    "parserKwarg",
]

doseMetavar = "<dose>[ unit]"
timeMetavar = "<time>[ unit]"
countMetavar = "<count>"
fracMetavar = "<decimal>"
hourMinuteMetavar = "<HHMM>"
dateMetavar = "<YYYYmmdd HHMM>"

parserKwarg = {}

# List of all command-line names in order of appearance
commandNames = [
    "man", "time", "date", "elapsed", "dose",
    "count", "lagtime", "t12abs", "linearabs", "t12a",
    "t12", "irfrac", "prodrug", "dr", "dr-max",
    "biphasic", "dist-time", "roa", "count", "minimum",
    "f", "p", "time-format", "msg", "file",
]
# Setting all argument values to keep appearance order
for cmd in commandNames:
    parserKwarg.update({cmd: None})
    del cmd

def addKwarg(name: str, summary: str, **kwargs):
    global parserKwarg
    _activeDict = {"help": summary}
    for k in kwargs:
        _activeDict[k] = kwargs.get(k)
    parserKwarg.update({name: _activeDict})#yay :D

# Adding half-life parameters (better approach)
for i in ["t12abs", "t12a", "t12"]:
    _label = "absorption" if i == "t12abs" else (
        "distribution" if i == "t12a" else "elimination"
    )
    addKwarg(i, "%s half-life" % _label, metavar=timeMetavar)

# Manually adding parameters (order here is arbitrary)
addKwarg("man", "displays the manual", action="store_true")
addKwarg("msg", "displays this message upon script execution", metavar="<msg>")
addKwarg("dose", "dose of the drug being simulated", metavar=doseMetavar)
addKwarg("count", "number of doses administered", metavar=countMetavar)
addKwarg("time", "time the dose was administered", metavar=timeMetavar)
addKwarg("elapsed", "time elapsed since drug administration", metavar=timeMetavar)
addKwarg("date", "date and time at drug administration", metavar=dateMetavar)
addKwarg("p", "decimal precision of drug concentration", metavar=fracMetavar, dest="precision", type=int)
addKwarg("f", "bioavailability of the drug being simulated", metavar=fracMetavar, dest="bioavailability")
addKwarg("irfrac", "fraction of dose which releases instantly", metavar=fracMetavar)
addKwarg("lagtime", "time taken for drug to reach systemic circulation", metavar=timeMetavar)
addKwarg("dr-max", "displays the maximum concentration achieved (accompanied by `dr`)", action="store_true")
addKwarg("biphasic", "uses biphasic elimination method", action="store_true")
addKwarg("time-format", "time format displayed upon simulation commencement", metavar="(12|24)")
addKwarg("minimum", "minimum concentration before simulation completion", metavar=doseMetavar)
addKwarg("roa", "route of administration", metavar="<route>")
addKwarg("prodrug", "fraction of prodrug converts into active drug", metavar=fracMetavar)
addKwarg("dr", "time second delayed release drug is released", metavar=timeMetavar)
addKwarg("dist-time", "time of distribution phase", metavar=timeMetavar)
addKwarg("linearabs", "uses linear absorption", action="store_true")
addKwarg("count", "number of doses administered", metavar="<n>")
addKwarg("file", "file containing drug information for the simulation", metavar="<file_location>")
