import json
import zipfile

import pandas as pd
from flask import request, flash, redirect, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from mongoengine import DoesNotExist

import utils
from constants import Constants, Messages, Errors
from database.experiment import Experiment
from handlers.dataHandler import DataHandler


class Home(Resource):
    def get(self):
        return "Home", 200


class DashboardApi(Resource):
    @jwt_required()
    def get(self):
        uid = get_jwt_identity()
        try:
            return Experiment.objects.get(uid=uid)
        except DoesNotExist:
            return []


class UploadExperimentApi(Resource):
    @jwt_required()
    def post(self):
        uid = get_jwt_identity()
        if Constants.UPLOAD_FILE_INPUT not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files[Constants.UPLOAD_FILE_INPUT]
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            result, error_msg = utils.handle_input(file, uid)
            if result:
                return jsonify(message=Messages.UserAddedSuccessfully), 201
            elif error_msg:
                return jsonify(message=Messages.UserAddedSuccessfully), 400
        return jsonify(message=Messages.UserAddedSuccessfully), 400


class GetExperimentApi(Resource):
    def get(self, experiment_id):
        experiment = Experiment.objects.get(id=experiment_id)
        try_count = 0
        while try_count < 5:
            try:
                return utils.organize_by_blocks(experiment[0]['timeline'],
                                                experiment[0]['count'],
                                                experiment[0]['name']), 200
            except Exception as e:
                print(str(e))
                continue
            finally:
                try_count += 1
        return jsonify(Errors.ExperimentDoesNotExit), 404

    def post(self, experiment_id):
        if request.data:
            try:
                loads_value = json.loads(request.data.decode('utf8'))
                to_upload = {
                    "result": loads_value
                }
                utils.upload_data(to_upload, experiment_id)
            except Exception as e:
                print(e)


class ExportExperimentResultApi(Resource):
    @jwt_required()
    def post(self):
        experiment_id = request.values.get("id_input")
        result_data_frame = pd.DataFrame()
        try:
            result_data_frame = DataHandler().export_experiment(experiment_id)
        except Exception as e:
            print("export bug: " + str(e))
            flash("There is a problem with export")
        finally:
            csv_file_name = "Experiment_Result.csv"
            result_data_frame.to_csv(csv_file_name, mode='w')
            return send_file(csv_file_name,
                             mimetype='text/csv',
                             attachment_filename=csv_file_name,
                             as_attachment=True)


class UploadImagesToExperimentApi(Resource):
    @jwt_required()
    def post(self):
        # check if the post request has the file part
        if 'imagesInput' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['imagesInput']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            name = request.values.get("name_input")
            if name is not None:
                extract_folder = "zip_folder/"
                zipfile.ZipFile(file).extractall(extract_folder)
                # x = threading.Thread(target=utils.extract_and_upload_stimulus,
                #                      args=(bucket, extract_folder, name,))
                # x.start()
