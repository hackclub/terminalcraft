# Installation

## Downloading and Running Binary

Check out the [releases](https://github.com/yousseftechdev/PostMaker/releases) section. PostMaker is available for Windows, Mac, and Linux.

## Running the Python Script Instead

### 1. Install Requirements

```sh
pip install requests termcolor rich
```

### 2. Run PostMaker

```sh
python main.py
```

## Included Dummy API

PostMaker comes with a dummy API (`dummyAPI.py`) built using Flask. This API provides various endpoints to test PostMaker's functionality, including support for different HTTP methods, status codes, redirects, authentication, and more.

To start the dummy API:
```sh
python tests/dummyAPI.py
```

You can also use the executable for easier use, Linux and Windows versions included.

Once running, you can use PostMaker to interact with the dummy API at `http://127.0.0.1:5000`.
