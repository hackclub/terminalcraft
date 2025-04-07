from requests import sessions
from iformat import iprint
from sys import argv

s = sessions.Session()

def make_request(method, url, json=None, **kwargs):
    response = s.__getattribute__(method)(url, json=json, **kwargs)
    if response.status_code//100 == 2:
        iprint(response.json())
    else:
        iprint(f"Error: {response.status_code}, {response.json().get('error') or response.text}")

if len(argv) < 2 and input("Create messages?"):
    make_request("post", "http://localhost:5000/api/messages", json={
        "convo_id": 0,
        "user_id": 0,
        "content": "Hello, World!"
    })

    make_request("post", "http://localhost:5000/api/messages", json={
        "convo_id": 0,
        "user_id": 1,
        "content": "Hello, World!"
    })

    make_request("post", "http://localhost:5000/api/messages", json={
        "convo_id": 1,
        "user_id": 1,
        "content": "Hello, World!"
    })

""" make_request("post", "http://localhost:5000/api/messages", json={
    "convo_id": 0,
    "user_id": 0,
    "content": "Hello, World!"
})

make_request("post", "http://localhost:5000/api/messages", json={
    "convo_ids": [0, 0],
    "user_ids": [0, 1],
    "contents": ["Hello, World!", "Hello, World!"]
}) """

make_request("post", "http://localhost:5000/api/users", json={
    "name": "billybob"
})

make_request("post", "http://localhost:5000/api/convos", json={
    "name": "test0"
})

make_request("post", "http://localhost:5000/api/convos", json={
    "name": "test1"
})

make_request("post", "http://localhost:5000/api/messages", json={
    "convo_id": 0,
    "user_id": 0,
    "content": "Im in convo 0"
})

make_request("post", "http://localhost:5000/api/messages", json={
    "convo_id": 1,
    "user_id": 0,
    "content": "Im in convo 1"
})

make_request("get", "http://localhost:5000/api/messages?convo_ids=0")

make_request("get", "http://localhost:5000/api/messages?convo_ids=1")