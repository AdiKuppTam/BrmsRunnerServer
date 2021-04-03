import os

import flask
from flask_jwt_extended import JWTManager
from flask_restful import Api

import __data__ as data
from constants import Constants, EnvironmentVariables
from routes.appRoutes import dashboard, upload_experiment, get_experiment, export_experiment_result, \
    upload_images_to_experiment
from routes.authRoutes import login, register

app = flask.Flask(data.__app_name__)
api = Api(app)

jwt = JWTManager(app)
app.config[Constants.JWT_SECRET_KEY] = os.environ[EnvironmentVariables.SECRET_KEY]


@app.route('/experiment/<path:path>')
def src(path=''):
    return path


@app.route('/experiment/gs://<path:path>')
def src_gs(path=''):
    return "gs://" + path


api.add_resource(login, '/login', methods=["POST"])
api.add_resource(register, '/register', methods=["POST"])

api.add_resource(dashboard, '/')
api.add_resource(upload_experiment, '/upload/<uid>', methods=["POST"])
api.add_resource(get_experiment, '/experiment/<experiment_id>', methods=["GET", "POST"])
api.add_resource(export_experiment_result, '/export', methods=["POST"])
api.add_resource(upload_images_to_experiment, '/upload_images', methods=["POST"])

if __name__ == '__main__':
    app.run(debug=True)
