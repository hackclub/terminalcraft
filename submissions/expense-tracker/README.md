# Expense Tracker

A terminal-based expense tracking application built with Python and Textual, designed to run on Windows, macOS, and Linux.

## Features
- Add, edit, and delete expenses with details (amount, currency, description, category).
- View monthly and yearly expense reports.
- Switch global currency (USD, INR) to convert expense amounts.
- Split-screen UI with a closable report pane.
- Cross-platform compatibility.

## Installation

### Prerequisites
- Python 3.9 or higher
- Git (optional, for cloning)

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/NotYourDoraemon/expense-tracker.git
   cd expense-tracker
   ```
2. Set up a virtual environment and install dependencies:
   - On macOS/Linux:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     pip install --upgrade pip
     pip install -r requirements.txt
     ```
   - On Windows (PowerShell):
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     pip install --upgrade pip
     pip install -r requirements.txt
     ```
3. Install the package:
   ```bash
   pip install .
   ```
4. Run the application:
   ```bash
   expense-tracker
   ```

## Usage
- **Add Expense**: Enter amount, select currency (USD/INR), description, and category, then click "Add".
- **View Reports**: Click "Monthly Report" or "Yearly Report" to see expenses in the right pane.
- **Edit Expense**: Click "Edit" next to an expense, modify details, and save.
- **Close Report**: Click the "X" at the top-right of the report pane.
- **Change Global Currency**: Use the dropdown at the top of the report pane to switch between USD and INR.

## Development
- **Dependencies**: Managed in `requirements.txt`. Updated to use `textual>=0.47.1` and `requests==2.31.0`.
- **Packaging**: Use `setup.py` to install as a package with the command `expense-tracker`.
- **Contributing**: Fork the repository, make changes, and submit a pull request.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements
- Built with [Textual](https://textual.textualize.io/) for the terminal UI.
- Developed by NotYourDoraemon.

## Update Notes
- Ensure `pip` is upgraded to the latest version (e.g., 25.0.1) for compatibility with the specified dependencies.
- Tested on Windows, macOS, and Linux environments.
