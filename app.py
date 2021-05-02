import os

from flask import send_from_directory, Flask
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_restful import Api

import __data__ as data
from constants import Constants, EnvironmentVariables
from assets.errors import errors
from database.db import initialize_db
from routes.all_routes import initialize_routes

app = Flask(data.__app_name__)
app.config[Constants.JWT_SECRET_KEY] = os.environ[EnvironmentVariables.SECRET_KEY]
app.config[Constants.MONGODB_SETTINGS] = {
    'host': os.environ[EnvironmentVariables.CONNECTION_STRING]
}
app.config['JWT_TOKEN_LOCATION'] = ['headers', 'query_string']

bcrypt = Bcrypt(app)
jwt = JWTManager(app)
api = Api(app)

initialize_db(app)
initialize_routes(api)


@app.route('/favicon.ico')
def icon():
    return send_from_directory(app.static_folder, 'favicon.ico', mimetype='image/vnd.microsoft.icon')
