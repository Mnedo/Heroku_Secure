import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Token(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'tokens'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    token = sqlalchemy.Column(sqlalchemy.String)
    app = sqlalchemy.Column(sqlalchemy.String)
