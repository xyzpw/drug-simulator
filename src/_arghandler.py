import re
import os

isFloatPattern = re.compile(r"^(?:(?:0)?\.\d+)$")
def validateArgs(args: dict):
    if args.get("units"):
        print("available units: (s)econds, (m)inutes, (h)ours, (d)ays")
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
        if not bool(isFloatPattern.search(args.get("bioavailability"))):
            fValue = float(args.get("bioavailability"))
            if not 1 > fValue > 0:
                raise SystemExit("bioavailability must be greater than 0 and less than 1")
    if args.get("dr_max"):
        if args.get("dr") == None:
            raise SystemExit("'dr_max' must be accompanied by 'dr'")
        if args.get("time") != None or args.get("elapse") != None:
            raise SystemExit("'dr_max' cannot be used with 'time' or 'elapse'")
        if args.get("dr_max") and args.get("probability"):
            raise SystemExit("'dr_max' and 'probability' cannot be used simultaneously")
    if args.get("clear"):
        #NOTE: Some terminals do not clear buffer. Use `os.system("printf '\e[3J' && clear")` if your terminal does not do this by default.
        os.system("clear" if os.name=="nt" else "clear")

#lolayylmao:DD