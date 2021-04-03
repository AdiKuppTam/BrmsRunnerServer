import json
import os
import zipfile

from flask import request, flash, redirect, jsonify, send_file
from flask_jwt_extended import jwt_required

import pandas as pd
from flask_restful import Resource
from pymongo import MongoClient

import utils
from constants import Constants, Messages, EnvironmentVariables, DBTables

conn_str = os.environ[EnvironmentVariables.CONNECTION_STRING]
client = MongoClient(conn_str)
db = client.test
user = db[DBTables.Users]


class Dashboard(Resource):
    @jwt_required
    def get(self, uid):
        lst = []
        collection = db.collection(u'Experiments')
        for document in collection.stream():
            doc_dict = document.to_dict()
            if "uid" in doc_dict and doc_dict["uid"] == uid:
                new_doc = [doc_dict["name"], str(document.id), doc_dict["count"]]
                lst.append(new_doc)
        return lst


class UploadExperiment(Resource):
    @jwt_required
    def post(self, uid):
        # check if the post request has the file part
        if Constants.UPLOAD_FILE_INPUT not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files[Constants.UPLOAD_FILE_INPUT]
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            result, error_msg = utils.handle_input(db, file, uid)
            if result:
                return jsonify(message=Messages.UserAddedSuccessfully), 201
            elif error_msg:
                return jsonify(message=Messages.UserAddedSuccessfully), 400
        return jsonify(message=Messages.UserAddedSuccessfully), 400


class GetExperiment(Resource):
    def get(self):
        # doc_ref = db.collection(u'Experiments').document(experiment_id)
        # experiment = doc_ref.get().to_dict()
        try_count = 0
        while try_count < 5:
            try:
                print("hello")
                # if experiment:
                #     timeline = utils.organize_by_blocks(experiment['timeline'],
                #                                         experiment['count'],
                #                                         bucket,
                #                                         experiment['name'])
                #     return render_template('experiment_html.html',
                #                            title='Experiment',
                #                            timeline=timeline,
                #                            background_color=experiment['background_color'])
            except Exception as e:
                print("Error: " + str(e))
                continue
            finally:
                try_count += 1
        return jsonify("Experiment does not exit"), 404

    def post(self, experiment_id):
        if request.data:
            try:
                loads_value = json.loads(request.data.decode('utf8'))
                to_upload = {
                    "result": loads_value
                }
                utils.upload_data(db, to_upload, experiment_id)
                doc_ref = db.collection(u'Experiments').document(experiment_id)
                experiment = doc_ref.get().to_dict()
                update = {
                    'count': experiment['count'] + 1
                }
                doc_ref.update(update)
            except Exception as e:
                print(e)


class ExportExperimentResult(Resource):
    @jwt_required
    def post(self):
        user_id = request.values.get("id_input")
        final_df = pd.DataFrame()
        try:
            final_df = utils.collection_to_csv(db.collection(user_id))
            if request.form.get('removeAllData'):
                utils.delete_collection(db.collection(user_id),
                                        utils.get_collection_count(db.collection(user_id).stream()))
        except Exception as e:
            print("export bug: " + str(e))
            flash("There is a problem with export")
        finally:
            csv_file_name = "Experiment_Result.csv"
            final_df.to_csv(csv_file_name, mode='w')
            return send_file(csv_file_name,
                             mimetype='text/csv',
                             attachment_filename=csv_file_name,
                             as_attachment=True)


class UploadImagesToExperiment(Resource):
    @jwt_required
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
