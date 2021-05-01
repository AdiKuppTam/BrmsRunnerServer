import os

from flask import send_from_directory, Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api

import __data__ as data
from constants import Constants, EnvironmentVariables
from routes.appRoutes import ExportExperimentResult, UploadExperiment, \
    UploadImagesToExperiment, GetExperiment, Dashboard, Home
from routes.authRoutes import Login, Register

app = Flask(data.__app_name__)
api = Api(app)

jwt = JWTManager(app)
app.config[Constants.JWT_SECRET_KEY] = os.environ[EnvironmentVariables.SECRET_KEY]


@app.route('/experiment/<path:path>')
def src(path=''):
    return path


@app.route('/experiment/gs://<path:path>')
def src_gs(path=''):
    return "gs://" + path


@app.route('/favicon.ico')
def icon():
    return send_from_directory(app.static_folder, 'favicon.ico', mimetype='image/vnd.microsoft.icon')


api.add_resource(Login, '/login')
api.add_resource(Register, '/register')

api.add_resource(Home, '/')
api.add_resource(Dashboard, '/dashboard/<uid>')
api.add_resource(UploadExperiment, '/upload/<uid>')
api.add_resource(GetExperiment, '/experiment/<experiment_id>')
api.add_resource(ExportExperimentResult, '/export')
api.add_resource(UploadImagesToExperiment, '/upload_images')

if __name__ == '__main__':
    app.run(debug=True)
