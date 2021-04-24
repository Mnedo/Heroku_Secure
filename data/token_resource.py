from flask_restful import abort, Resource
from . import db_session
from .token import Token
from flask import jsonify


def abort_if_user_not_found(app_name):
    session = db_session.create_session()
    app = session.query(Token).filter(Token.app == app_name).first()
    if not app:
        abort(404, message=f"App {app_name} not found")


class TokenResource(Resource):
    def get(self, app_name):
        abort_if_user_not_found(app_name)
        session = db_session.create_session()
        app = session.query(Token).filter(Token.app == app_name).first()
        return app.token
