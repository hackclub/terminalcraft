from setuptools import setup, find_packages

setup(
    name="expense-tracker",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "textual>=0.47.1",
        "requests==2.31.0",
    ],
    entry_points={
        "console_scripts": [
            "expense-tracker = expense_tracker.main:run_expense_tracker",
        ],
    },
    author="NotYourDoraemon",
    description="A terminal-based expense tracking application",
    python_requires=">=3.9",
)