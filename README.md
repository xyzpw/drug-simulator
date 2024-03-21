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

Optionally, you can use the `lineara` option if you prefer to not use absorption half-lives or don't know the value:
```bash
$ ./drug-simulator.py --lineara
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
Within the drug simulation program, you have the option to simulate delayed release drugs. For instance, consider Adderall XR, which has an instant release component of 50%, while the remaining 50% is intended to be released 4 hours later. Furthermore, you can utilize the 'lagtime' feature to introduce a delay in the simulation start, accounting for the time it takes the drug to reach the absorption phase after administration, e.g. pill ingestion.<br>
Example:
```bash
$ ./drug-simulator.py --lagtime 5m --dr 4h
```
Another example is coffee, which, on average, contains 80 mg of caffeine per serving.<br>
 Research suggest liquids take 2-5 minutes to appear in plasma:
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
## Contributing
Contributing small code changes such as bug fixes could be acceptable.
## See Also
https://en.wikipedia.org/wiki/Pharmacokinetics<br>
https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3351614/
