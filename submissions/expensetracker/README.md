# Python-BudgetTracker
A budget tracking program written in Python with visualisation

## Features
- **Set budget**
- **Add expenses**
- **Pie chart visualisation**
- **Data import & export**

## Setup

Clone this repo

cd into the directory
```
pip install matplotlib
python budget.py
```

### Visualised Chart

![chart](https://github.com/user-attachments/assets/ad145544-00c7-4f7d-8411-480b8049d7cb)


## Info

```
python budget.py set-budget 500 (Set total budget)
python budget.py add-expense BLAHAJ 20 (Add your expenses)
python budget.py summarise (Show the data in the terminal)
python budget.py --export-chart=CHARTNAME.png visualise (Generate a pie chart and export to the the file name specified)
python budget.py export budget_backup.json (Export data to the file specified)
python budget.py import budget_backup.json (Import data from the file specified)
```
