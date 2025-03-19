# Postperson
Who needs Postman when you can use a ripoff (in terminal though)?

## Installation

1. Clone the repo

```bash
git clone https://github.com/tathyagarg/postperson.git
cd postperson
```

2. Create and activate a virtual environment

### For Windows
```bash
python -m venv venv
venv\Scripts\activate
```

### For MacOS/Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install the dependencies

```bash
pip install -r requirements.txt
```

4. Run the script

```bash
python -m postperson
```

## Usage

Postperson stores your session data in JSON files. You can create a new session or load an existing one. You can then make requests to the server using the session data.
