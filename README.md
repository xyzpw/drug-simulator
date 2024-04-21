# drug-simulator
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/xyzpw/drug-simulator/total)
![GitHub repo size](https://img.shields.io/github/repo-size/xyzpw/drug-simulator)

Simulate the absorption and elimination of drugs in real time using *real* pharmacokinetic formulas.<br>

![drug-simulator-preview](https://github.com/xyzpw/drug-simulator/assets/76017734/6c39d9f5-2b8b-4aa4-a056-81cf2711c077)
## What It Does
The program will display the concentration of the drug at an increasing rate during the absorption phase. The displayed concentration will begin decreasing subsequent to the tmax (time to peak concentration).

## Prerequisites
- Terminal supporting ANSI codes

## Usage
Firstly, you should display the help menu to list additional options:
```bash
$ python3 drug-simulator.py --help
```

To execute the script in Linux via `./drug-simulator.py`, you must add execution perms:
```bash
$ chmod +x drug-simulator.py
```

### User Input
Starting the script without arguments will ask for a few prompts about the drug being simulated:
```text
dose:
tmax:
absorption half-life:
half-life:
```

After the information has been given, the simulation will start.<br>

Optionally, you can use the `linearabs` option if you prefer not to use absorption half-lives or don't know the value:
```bash
$ ./drug-simulator.py --linearabs
```

#### Time Units
When entering the time, units are by default set to seconds.<br>
Below are some examples for time units:
```text
1 s, 1 second, 1 seconds
1 h, 1 hour, 1 hours
1 d, 1 day, 1 days
```
Using a space between time and units are optional, therefor, 1s and 1 second are equivalent.

#### Arguments
Optionally, you can use arguments prior to the script commencement, e.g.<br>
`./drug-simulator.py --dose 60` will skip the `dose:` prompt because it has already been given as an argument.<br>

#### Timing
You can start the simulation at a specified time instead of starting once the script starts:
```text
./drug-simulator.py --time "13:00" # initiates the simulation at 1pm
./drug-simulator.py --elapse "1:30" # initiates the simulation 1.5 hours prior to the program commencement
```

#### Delayed Release and Lag Time
Within **drug-simulator**, there is an ability to simulate delayed release drugs, for example, consider Adderall XR, 50% of it releases instantly, while the remaining 50% is intended to release 4 hours later. Furthermore, you can use the `lagtime` argument which will have a countdown before the absorption phase begins, accounting for the time it takes the administered drug to reach the systemic circulation, e.g. pill ingesting for example.
```bash
$ ./drug-simulator.py --lagtime 5m --dr 4h
```
Another example is coffee, which, on average, contains 80 mg of caffeine per serving.<br>
 Research suggests liquids take 2-5 minutes to appear in plasma:
```bash
$ ./drug-simulator.py --lagtime 2m
```

#### Custom Messages
You can use custom messages at the beginning of the script with the `msg` argument. This can be used if you have multiple terminals open and want to keep track of what you are simulating:
```bash
$ ./drug-simulator.py --msg "anything can go here"
```

#### Reading From File
Pharmacokinetic information can be read through a file within the same directory:
```bash
$ ./drug-simulator.py --file "pharmacokinetic_example.json"
```
> [!NOTE]
> Adding ".json" is optional

#### Biphasic Elimination
When a drug is administered intravenously, it has an initial shorter half-life (called distribution or alpha half-life) as it is being distributed throughout the body. Subsequent to pseudo-equilibrium, the longer half-life (called terminal or beta half-life) is used.<br>

Usage example for simulating a bolus i.v. injection:
```bash
$ ./drug-simulator.py --tmaxed --t12 0.9m --t12a 0.3m --dist_time 1.5m --dose 1.3mg -p 3
```
> [!TIP]
> You may also use "--biphasic" alone, which will prompt for the distribution half-life and time in contrast to using it via arguments.

## Contributing
Contributing small code changes such as bug fixes could be acceptable.<br>

If any bugs, inaccuracies, or typos are found, be sure to report them via issues.

## See Also
https://en.wikipedia.org/wiki/Pharmacokinetics<br>
https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3351614/
