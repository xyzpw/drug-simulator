import re
import os
import argparse

__all__ = [
    "validateArgs",
    "createArgs",
]

def addCountToMsg(msg: str, count: bool):
    return "%dx %s" % (count, msg) if count.is_integer() else "%sx %s" % (count, msg)

def validateArgs(args: dict):
    if args.get("count") != 1 and args.get("msg") != None:
        _count: bool = args.get("count")
        args["msg"] = addCountToMsg(args.get("msg"), _count)
    if args.get("units"):
        availableUnitsStr = """time units: s(econds), m(inutes), h(ours), d(ays)
        \rmass units: mg, milligram(s), ug, mcg, microgram(s), g, gram(s)"""
        print(availableUnitsStr)
        raise SystemExit(0)
    if args.get("irfrac") != None and args.get("dr") == None:
        raise SystemExit("irfrac must be accompanied by delayed release")
    if args.get("irfrac") != None:
        irfracFloat = float(args.get("irfrac"))
        if not 1 >= irfracFloat >= 0:
            raise SystemExit("irfrac must be greater than 0 and less than 1")
    if args.get("tmaxed") and args.get("lagtime") != None:
        raise SystemExit("tmaxed and lagtime cannot be active simultaneously")
    if args.get("precision") != None:
        if not str(args.get("precision")).isnumeric():
            raise SystemExit("precision must be an integer")
        if int(args.get("precision")) not in range(0, 15+1):
            raise SystemExit("precision must be from 0 to 15")
    if args.get("probability") and args.get("linear"):
        raise SystemExit("probability and linear cannot be used simultaneously")
    if args.get("time") != None and args.get("elapse") != None:
        raise SystemExit("time and elapse cannot be used simultaneously")
    if args.get("bioavailability") != None:
        fValue = args.get("bioavailability")
        if not 1 >= fValue > 0:
            raise SystemExit("bioavailability must be greater than 0 and no more than 1")
    if args.get("dr_max"):
        if args.get("dr") == None:
            raise SystemExit("'dr_max' must be accompanied by 'dr'")
        if args.get("dr_max") and args.get("probability"):
            raise SystemExit("'dr_max' and 'probability' cannot be used simultaneously")
    if (args.get("biphasic") or args.get("t12a") != None or args.get("dist_time")) and args.get("probability"):
        raise SystemExit("biphasic and probability method cannot be used simultaneously")
    if args.get("clear"):
        #NOTE: Some terminals do not clear buffer. Use `os.system("printf '\e[3J' && clear")` if your terminal does not do this by default.
        os.system("clear" if os.name=="nt" else "clear")

def createArgs():
    parser = argparse.ArgumentParser(
        description="description: Simulates the absorption and elimination of drugs.",
        add_help=False,
    )
    parser.add_argument("--help", "-h", help="displays help and exits", action="help")
    parser.add_argument("--units", help="displays available time units [default: seconds]", action="store_true")
    parser.add_argument("--dose", help="the dosage to be simulated", metavar="<dose>[ unit]")
    parser.add_argument("--tmax", help="time it takes to reach peak concentration", metavar="<time>[ unit]")
    parser.add_argument("--t12abs", help="absorption half-life of the drug to be simulated", metavar="<time>[ unit]")
    parser.add_argument("--t12", help="half-life of the drug to be simulated", metavar="<time>[ unit]")
    parser.add_argument("--probability", help="display concentration as probability of drug remaining", action="store_true")
    parser.add_argument("--linear", help="calculates and uses elimination constant of given half-life", action="store_true")
    parser.add_argument("--linearabs", help="uses linear absorption regardless of method", action="store_true")
    parser.add_argument("--time", help="time the dose was administered in 24-hour format", metavar="HH:MM")
    parser.add_argument("--elapse", help="how much time has passed since the simulation was started", metavar="HH:MM")
    parser.add_argument("--tmaxed", help="starts simulation assuming the drug has already peaked", action="store_true")
    parser.add_argument("-p", help="decimal places to keep for displayed results", metavar="decimal_precision", dest="precision", default=0, type=int)
    parser.add_argument("-f", help="bioavailability of the drug being simulated",
        metavar="decimal", dest="bioavailability",
        type=float
    )
    parser.add_argument("--autocomplete", help="immediately exits once concentration reaches 0", action="store_true")
    parser.add_argument("--dr", help="duration until second part of dose is released (delayed release form)", metavar="<time>[ unit]")
    parser.add_argument("--irfrac", help="fraction of dose that is instant release (used with dr)", metavar="decimal")
    parser.add_argument("--lagtime", help="time taken for drug to appear", metavar="<time>[ unit]")
    parser.add_argument("--dr_max", help="displays the maximum achieved concentration since starting the simulation", action="store_true")
    parser.add_argument("--clear", help="clears the screen prior to script commencement", action="store_true")
    parser.add_argument("--msg", help="custom message on start", metavar="<msg>")
    parser.add_argument("--file", help="reads pharmacokinetic information from a json file", metavar="<file_name>")
    parser.add_argument("--count", help="number of doses administered", metavar="N", default=1, type=float)
    parser.add_argument("--t12a", help="distribution half-life of the drug to be simulated", metavar="<time>[ unit]")
    parser.add_argument("--dist_time", help="time it takes to complete the distribution phase", metavar="<time>[ unit]")
    parser.add_argument("--biphasic", help="uses a biphasic elimination method", action="store_true")
    parser.add_argument("--time_format", help="time format displayed upon simulation commencement", metavar="(12|24)")
    return parser

#lolayylmao:DD