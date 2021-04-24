import os
from flask import Flask
from flask_restful import Api
from data import db_session, token_resource
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
db_session.global_init("db/tokens.db")
db_sess = db_session.create_session()
api = Api(app)
api.add_resource(token_resource.TokenResource, '/api/token/<string:app_name>')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
