from flask import Flask, request
from flask_restful import Resource, Api, abort, fields, marshal
from functools import wraps
from iformat import iprint

from utils import default501, _always_in

app = Flask(__name__)
api = Api(app)

api.prefix = "/api"

message_fields = {
    "message_id": fields.Integer,
    "convo_id": fields.Integer,
    "user_id": fields.Integer,
    "content": fields.String
}

class MessageList:
    def __init__(self):
        self.message_id = -1
        self.messages = []

    def _get_next_message_id(self):
        self.message_id += 1
        return self.message_id

    def query_filter(func):
        def wrapper(self, start=0, end=None, max_results=None, convo_ids=_always_in(), user_ids=_always_in(), message_ids=None):
            if message_ids:
                res = list(filter(lambda m: m.message_id in message_ids, self.messages[start:end]))
            else:
                res = list(filter(lambda m: m.convo_id in convo_ids and m.user_id in user_ids, self.messages[start:end]))
            max_results = len(res) if max_results == None else max_results
            return func(self, res[-max_results:])
        return wrapper

    @query_filter
    def query_get(self, messages):
        return messages

    def query_add(self, message):
        message.message_id = self._get_next_message_id()
        self.messages.append(message)
        return message

    def query_update(self, message_id, content):
        for message in self.messages:
            if message.message_id == message_id:
                message.content = content
                return message
        return None

    @query_filter
    def query_delete(self, messages):
        for message in messages:
            self.messages.remove(message)

msgs_list = MessageList()

class Message(default501):
    def get(self, message_id):
        msgs = msgs_list.query_get(message_ids=[message_id])
        if msgs is None or len(msgs) == 0:
            return {"error": f"Message {message_id} does not exist"}, 404
        return marshal(msgs[0], message_fields)

class Messages(default501):
    def get(self):
        try:
            message_ids = [int(id) for id in request.args.get("message_ids", "").split(",") if id]
        except Exception as e:
            return {"error": "Invalid value for message_ids"}, 400
        try:
            convo_ids = [int(id) for id in request.args.get("convo_ids", "").split(",") if id] or _always_in()
        except ValueError:
            return {"error": "Invalid value for convo_ids"}, 400
        try:
            user_ids = [int(id) for id in request.args.get("user_ids", "").split(",") if id] or _always_in()
        except ValueError:
            return {"error": "Invalid value for user_ids"}, 400
        try:
            start = int(request.args.get("start", 0))
        except ValueError:
            return {"error": "Invalid value for start"}, 400
        try:
            end = int(v) if (v:=request.args.get("end", None)) else None
        except ValueError:
            return {"error": "Invalid value for end"}, 400

        return [marshal(m, message_fields) for m in msgs_list.query_get(start=start, end=end, convo_ids=convo_ids, user_ids=user_ids, message_ids=message_ids)]

    def post(self):
        try:
            convo_ids = [int(i) for i in (request.json.get("convo_ids") or [request.json.get("convo_id")])]
        except ValueError:
            return {"error": "Invalid value for convo_id(s)"}, 400
        try:
            user_ids = [int(i) for i in (request.json.get("user_ids") or [request.json.get("user_id")])]
        except ValueError:
            return {"error": "Invalid value for user_id"}, 400
        contents = request.json.get("contents") or [request.json.get("content")]
        if len(convo_ids) != len(user_ids) or len(convo_ids) != len(contents):
            return {"error": "All fields must contain the same number of items"}, 400
        invalid_options = [[], None, [None]]
        if convo_ids in invalid_options or user_ids in invalid_options or contents in invalid_options:
            return {"error": "Missing required fields"}, 400
        ids = []
        for convo_id, user_id, content in zip(convo_ids, user_ids, contents):
            m = Message()
            m.convo_id = convo_id
            m.user_id = user_id
            m.content = content
            ids.append(msgs_list.query_add(m).message_id)
        return {"message_ids": ids}

user_fields = {
    "user_id": fields.Integer,
    "name": fields.String
}

class UserList:
    def __init__(self):
        self.user_id = -1
        self.users = []

    def _get_next_user_id(self):
        self.user_id += 1
        return self.user_id

    def query_filter(func):
        def wrapper(self, start=0, end=None, max_results=None, user_ids=None):
            if user_ids:
                res = list(filter(lambda m: m.user_id in user_ids, self.users[start:end]))
            else:
                return self.users[start:end]
            max_results = len(res) if max_results == None else max_results
            return func(self, res[-max_results:])
        return wrapper

    @query_filter
    def query_get(self, users):
        return users

    def query_add(self, user):
        user.user_id = self._get_next_user_id()
        self.users.append(user)
        return user

    def query_update(self, user_id, name):
        for user in self.users:
            if user.user_id == user_id:
                user.name = name
                return user
        return None

    @query_filter
    def query_delete(self, users):
        ids = []
        for user in users:
            ids.append(user.user_id)
            self.users.remove(user)
        return ids
    
users_list = UserList()

class User(default501):
    def get(self, user_id):
        users = users_list.query_get(user_ids=[user_id])
        if users is None or len(users) == 0:
            return {"error": f"User {user_id} does not exist"}, 404
        return marshal(users[0], user_fields)

    def put(self, user_id):
        name = request.json.get("name")
        if name is None:
            return {"error": "Missing required field"}, 400
        u = users_list.query_update(user_id, name)
        if u is None:
            return {"error": f"User {user_id} does not exist"}, 404
        return marshal(u, user_fields)

    def delete(self, user_id):
        deleted_ids = users_list.query_delete(user_ids=[user_id])
        if len(deleted_ids) == 0:
            return {"error": f"User {user_id} does not exist"}, 404
        return {"user_id": deleted_ids[0]}

class Users(default501):
    def get(self):
        try:
            user_ids = [int(id) for id in request.args.get("user_ids", "").split(",") if id] or None
        except ValueError:
            return {"error": "Invalid value for user_ids"}, 400
        try:
            start = int(request.args.get("start", 0))
        except ValueError:
            return {"error": "Invalid value for start"}, 400
        try:
            end = int(v) if (v:=request.args.get("end", None)) else None
        except ValueError:
            return {"error": "Invalid value for end"}, 400

        return [marshal(u, user_fields) for u in users_list.query_get(start=start, end=end, user_ids=user_ids)]
    
    def post(self):
        # TODO: Implement bulk creation
        name = request.json.get("name")
        if name is None:
            return {"error": "Missing required field"}, 400
        u = User()
        u.name = name
        return {"user_id": users_list.query_add(u).user_id}
    
    def delete(self):
        try:
            user_ids = [int(id) for id in request.json.get("user_ids", "").split(",") if id] or None
        except ValueError:
            return {"error": "Invalid value for user_ids"}, 400
        if user_ids is None:
            return {"error": "Missing required field"}, 400
        return {"user_ids": users_list.query_delete(user_ids=user_ids)}

convo_fields = {
    "convo_id": fields.Integer,
    "name": fields.String
}

class ConvoList:
    def __init__(self):
        self.convo_id = -1
        self.convos = []

    def _get_next_convo_id(self):
        self.convo_id += 1
        return self.convo_id

    def query_filter(func):
        def wrapper(self, start=0, end=None, max_results=None, convo_ids=None):
            if convo_ids:
                res = list(filter(lambda m: m.convo_id in convo_ids, self.convos[start:end]))
            else:
                return self.convos[start:end]
            max_results = len(res) if max_results == None else max_results
            return func(self, res[-max_results:])
        return wrapper

    @query_filter
    def query_get(self, convos):
        return convos

    def query_add(self, convo):
        convo.convo_id = self._get_next_convo_id()
        self.convos.append(convo)
        return convo

    def query_update(self, convo_id, name):
        for convo in self.convos:
            if convo.convo_id == convo_id:
                convo.name = name
                return convo
        return None

    @query_filter
    def query_delete(self, convos):
        ids = []
        for convo in convos:
            ids.append(convo.convo_id)
            self.convos.remove(convo)
        return ids

convos_list = ConvoList()

class Convo(default501):
    def get(self, convo_id):
        convos = convos_list.query_get(convo_ids=[convo_id])
        if convos is None or len(convos) == 0:
            return {"error": f"Convo {convo_id} does not exist"}, 404
        return marshal(convos[0], convo_fields)

    def put(self, convo_id):
        name = request.json.get("name")
        if name is None:
            return {"error": "Missing required field"}, 400
        c = convos_list.query_update(convo_id, name)
        if c is None:
            return {"error": f"Convo {convo_id} does not exist"}, 404
        return marshal(c, convo_fields)
    
    def delete(self, convo_id):
        deleted_ids = convos_list.query_delete(convo_ids=[convo_id])
        if len(deleted_ids) == 0:
            return {"error": f"Convo {convo_id} does not exist"}, 404
        return {"convo_id": deleted_ids[0]}

class Convos(default501):
    def get(self):
        try:
            convo_ids = [int(id) for id in request.args.get("convo_ids", "").split(",") if id] or None
        except ValueError:
            return {"error": "Invalid value for convo_ids"}, 400
        try:
            start = int(request.args.get("start", 0))
        except ValueError:
            return {"error": "Invalid value for start"}, 400
        try:
            end = int(v) if (v:=request.args.get("end", None)) else None
        except ValueError:
            return {"error": "Invalid value for end"}, 400

        return [marshal(c, convo_fields) for c in convos_list.query_get(start=start, end=end, convo_ids=convo_ids)]
    
    def post(self):
        # TODO: Implement bulk creation
        name = request.json.get("name")
        if name is None:
            return {"error": "Missing required field"}, 400
        c = Convo()
        c.name = name
        return {"convo_id": convos_list.query_add(c).convo_id}

    def delete(self):
        try:
            convo_ids = [int(id) for id in request.json.get("convo_ids", "").split(",") if id] or None
        except ValueError:
            return {"error": "Invalid value for convo_ids"}, 400
        if convo_ids is None:
            return {"error": "Missing required field"}, 400
        return {"convo_ids": convos_list.query_delete(convo_ids=convo_ids)}

class ConvoUser(default501):
    pass

class ConvoUsers(default501):
    pass

api.add_resource(Message, "/messages/<int:message_id>", endpoint="message")
api.add_resource(Messages, "/messages", endpoint="messages")

api.add_resource(User, "/users/<int:user_id>", endpoint="user")
api.add_resource(Users, "/users", endpoint="users")

api.add_resource(Convo, "/convos/<int:convo_id>", endpoint="convo")
api.add_resource(Convos, "/convos", endpoint="convos")

api.add_resource(ConvoUser, "/convos/<int:convo_id>/users/<int:user_id>", endpoint="convo_user")
api.add_resource(ConvoUsers, "/convos/<int:convo_id>/users", endpoint="convo_users")

@app.errorhandler(404)
def page_not_found(e):
    return {"error": "The requested URL was not found."}, 404

if __name__ == "__main__":
    app.run()
