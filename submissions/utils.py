from flask_restful import Resource

class default501(Resource):
    def get(self, *args, **kwargs):
        return {"error": "GET not yet implemented for this endpoint"}, 501

    def post(self, *args, **kwargs):
        return {"error": "POST not yet implemented for this endpoint"}, 501

    def put(self, *args, **kwargs):
        return {"error": "PUT not yet implemented for this endpoint"}, 501

    def delete(self, *args, **kwargs):
        return {"error": "DELETE not yet implemented for this endpoint"}, 501

class _always_in(list):
    def __contains__(self, key):
        return True