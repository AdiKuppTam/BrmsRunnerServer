import ast
import os
import flask
import json
import pandas as pd
import zipfile
import utils
from flask import render_template, request, redirect, flash, send_file, Response, jsonify
import __data__ as data
from pymongo import MongoClient
from constants import Constants, EnvironmentVariables
from flask_jwt_extended import JWTManager, jwt_required, create_access_token

app = flask.Flask(data.__app_name__)
jwt = JWTManager(app)
app.config[Constants.JWT_SECRET_KEY] = EnvironmentVariables.SECRET_KEY

conn_str = os.environ[EnvironmentVariables.CONNECTION_STRING]
client = MongoClient(conn_str)
db = client.test
user = db["User"]


@app.route("/register", methods=["POST"])
def register():
    email = request.form["email"]
    # test = User.query.filter_by(email=email).first()
    test = user.find_one({"email": email})
    if test:
        return jsonify(message="User Already Exist"), 409
    else:
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        password = request.form["password"]
        user_info = dict(first_name=first_name, last_name=last_name, email=email, password=password)
        user.insert_one(user_info)
        return jsonify(message="User added successfully"), 201


@app.route("/login", methods=["POST"])
def login():
    if request.is_json:
        email = request.json["email"]
        password = request.json["password"]
    else:
        email = request.form["email"]
        password = request.form["password"]

    test = user.find_one({"email": email, "password": password})
    if test:
        access_token = create_access_token(identity=email)
        return jsonify(message="Login Succeeded!", access_token=access_token), 201
    else:
        return jsonify(message="Bad Email or Password"), 401


@app.route('/experiment/<path:path>')
def src(path=''):
    return path


@app.route('/experiment/gs://<path:path>')
def src_gs(path=''):
    return "gs://" + path


@app.route('/dashboard/<uid>')
@jwt_required
def dashboard(uid):
    lst = []
    collection = db.collection(u'Experiments')
    for document in collection.stream():
        doc_dict = document.to_dict()
        if "uid" in doc_dict and doc_dict["uid"] == uid:
            new_doc = [doc_dict["name"], str(document.id), doc_dict["count"]]
            lst.append(new_doc)
    return lst


@app.route('/delete_experiment', methods=["POST"])
@jwt_required
def delete():
    experiment_id = request.json.get("value")
    experiment_name = db.collection(u'Experiments').document(experiment_id).get().to_dict()["name"]
    # utils.delete_stimulus_folder(bucket, experiment_name)
    db.collection(u'Experiments').document(experiment_id).delete()


@app.route("/upload/<uid>", methods=["POST"])
@jwt_required
def upload(uid):
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
            return Response(status=200)
        elif error_msg:
            return Response(status=400, response=error_msg)
    return Response(status=400)


@app.route('/experiment/<experiment_id>', methods=["GET", "POST"])
def get_experiment(experiment_id):
    if request.method == "POST":
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
    else:
        doc_ref = db.collection(u'Experiments').document(experiment_id)
        experiment = doc_ref.get().to_dict()
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
        return render_template('experiment_does_not_exist.html',
                               title='Psychology Experiment')


@app.route('/export', methods=["POST"])
@jwt_required
def export_experiment_result():
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


@app.route('/upload_images', methods=["POST"])
@jwt_required
def upload_images_to_experiment():
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


if __name__ == '__main__':
    app.run(debug=True)