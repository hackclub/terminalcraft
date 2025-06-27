# GraphCalc

## About

I consider Desmos funni, so I decided to bring a similar graphing calculator to the terminal!
I originally didn't want to bother with pyinstaller, so I didn't even use regex and instead coded parsing logic myself.
The program takes in a math function (currently limited in operator support, i plan on adding more math functions later) and samples its value at multiple points.
The values are then saved as a .csv and the program renders them with a bar graph

## Options

- `--function` basic mathematic expression including x. the default (for quick testing) is `x*x/4`.
- `--x-offset` positive integer, moves the "frame of sampling"
- `--x-range` range over which the program should sample, default is 8
- `--sample` number of samples to use, default is 16
- `--file` file for csv output, default is `function.csv`
**Run options:**
- `--run`, invokes `termgraph(.py)` after outputting the csv values
- `--x-space` space available for x axis in terminal, default is 86 to support small terminals, 126 and 168 work well.
- `--label` provides `termgraph` with x axis labels for each sample

## Installation

**Pyinstaller**
Download both `termgraph` and `termgraph-calc` from the pybuilds folder and place them in the same folder.


**Windows**
Run `pip install argparse`
Download both `termgraph.py` and `termgraph-calc.py` from the root folder and place them in the same folder.


**Linux/macOS**
Download both `termgraph.py` and `termgraph-calc.py` from the root folder and place them into a folder of your choice.
In that folder, run
```
python3 -m venv .venv
source .venv/bin/activate
pip install argparse
```
To start the program in the venv, run 
```
source .venv/bin/activate
python3 termgraph-calc.py
```
