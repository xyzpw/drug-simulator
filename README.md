# drug-simulator
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/xyzpw/drug-simulator/total)
![GitHub repo size](https://img.shields.io/github/repo-size/xyzpw/drug-simulator)

**drug-simulator** is a program designed to simulate drug concentrations in real time using user-prompted values.

<img width="664px" height="400px" src="https://github.com/user-attachments/assets/b872064c-1b9d-4672-b9b1-14f071c28b62"/>

## How it Works
The program prompts for values which will be used to calculate and display drug concentrations in real time to the terminal.<br>
Several options can be used which effect these results, such as route of administration.

## Usage
Executing the script:
```bash
$ python3 drug-simulator.py
```

Or add execution perms:
```bash
$ chmod +x drug-simulator.py
```

Which will allow you to run it via:
```bash
$ ./drug-simulator.py
```

Run help to see additional usage:
```bash
$ ./drug-simulator.py --help
```

### User Input
Upon running the script, required values will be prompted for input. Given that the script was run without additional arguments, the simulation assumes IV bolus, which will prompt the following values:
```txt
dose:
half-life:
```

The default time unit is seconds, to change this, type in the unit after the time digit, e.g. "9 hours" or "9h" for 9 hours.<br>
Dose units can also be used.

The simulation will begin upon entering the last required value.

### Route of Administration
Different routes of administration can be simulated with the `roa` argument:
```bash
$ ./drug-simulator.py --roa route
```

#### IV Bolus
IV bolus will be used by default.

#### Oral
Changing the route of administration will also alter the values required to begin the simulation.<br>
In this case, the following prompts will be displayed:

```txt
dose:
bioavailability:
absorption half-life:
half-life:
```

##### Delayed Release
Delayed release drugs can be simulated where a specific fraction of the drug is released instantly and some time before the next dose. For example, Adderall XR has 50% of the beads release instantly, and the other half is intended to release 4 hours later.
```bash
$ ./drug-simulator.py --roa oral-dr --dr 4h --irfrac 0.5 --msg "adderall xr"
```

Additionally, `dr-max` can be used to display the highest concentration achieved since the simulation has started:
```bash
$ ./drug-simulator.py --roa oral-dr --dr 4h --irfrac 0.5 --dr-max
```

##### Prodrug
Prodrug/active drug concentrations can be *estimated* using oral route of administration:
```bash
$ ./drug-simulator.py --roa oral-prodrug -f 0.964 --prodrug 0.297 --msg vyvanse
```

> [!NOTE]
> The active drug concentration are estimates and not precise!

### Lagtime
The lagtime feature can be used to start a countdown before the absorption phase begins, this can account for the time it takes a drug to reach the systemic circulation, e.g. pill ingesting.<br>
For example, water takes 2&#8211;5 minutes to reach plasma after ingestion.
```bash
$ ./drug-simulator.py --roa oral --dose "80 mg" --lagtime 2m --msg "caffeine from coffee"
```

### Timing
The simulation can be started assuming administration occurred prior to the simulation commencement.

Start at a specific time:
```bash
$ ./drug-simulator.py --time 0554
$ ./drug-simulator.py --time "5:54 am"
```

Administration at a specific date:
```bash
$ ./drug-simulator.py --date "20240808 1922"
$ ./drug-simulator.py --date "08/08/2024 7:22 pm"
```

Elapsed time since administration:
```bash
# 72 hours post-dose
$ ./drug-simulator.py --elapsed 7200
```

These options will take into account `lagtime` if it is used.

### Custom Messages
Custom messages can be used, for example, if you have multiple simulations running and want to keep track of each:
```bash
$ ./drug-simulator.py --msg "anything can go here"
```

### Reading Files
Pharmacokinetic information can be stored in a json file to prevent user-input prompts:
```bash
$ ./drug-simulator.py --file pharmacokinetic_example
```

> [!TIP]
> ".json" is optional

## Contributing
For any typos, bugs, or inaccuracies found, report this in issues.<br>
Code contributions might be accepted if they do not include:
- changes to formulas
- major changes
- changes to usage

## See Also
https://en.wikipedia.org/wiki/Pharmacokinetics<br>
https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3351614/
