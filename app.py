import flask
import json
import pandas as pd
import zipfile
import threading
import utils
from firebase_admin import credentials, initialize_app, storage, firestore
from flask import render_template, request, redirect, flash, send_file
import __data__ as data

app = flask.Flask(data.__app_name__)
app.config.update(
    prog=f'{data.__name__} v{data.__version__}',
    author=data.__author__
)

cred = credentials.Certificate("popup-firebase.json")
initialize_app(cred, {'storageBucket': 'popup-965c9.appspot.com'})

bucket = storage.bucket()
db = firestore.client()


@app.route('/experiment/<path:path>')
def src(path=''):
    return path


@app.route('/upload/experiment/<path:path>')
def src_from_upload(path=''):
    return redirect("experiment/" + path)


@app.route('/experiment/gs://<path:path>')
def src_gs(path=''):
    return "gs://" + path


@app.route('/dashboard/<uid>')
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
def delete():
    experiment_id = request.json.get("value")
    experiment_name = db.collection(u'Experiments').document(experiment_id).get().to_dict()["name"]
    utils.delete_stimulus_folder(bucket, experiment_name)
    db.collection(u'Experiments').document(experiment_id).delete()


@app.route("/upload/<uid>", methods=["GET", "POST"])
def upload(uid):
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file_input' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file_input']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            result, error_msg = utils.handle_input(db, file, uid)
            if result:
                return render_template("upload.html",
                                       title="Upload",
                                       value="Experiment Created",
                                       visible="visible",
                                       h2color="green",
                                       link="/experiment/" + str(result),
                                       linkExist="visibility")
            elif error_msg:
                return render_template("upload.html",
                                       title="Upload",
                                       visible="visible",
                                       h2color="red",
                                       linkExist="collapse",
                                       value=error_msg)

        return render_template("upload.html",
                               title="Upload",
                               visible="visible",
                               value="There is an error",
                               linkExist="collapse")
    else:
        return render_template("upload.html",
                               value="-",
                               visible="hidden",
                               linkExist="collapse",
                               title="Upload")


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
                if experiment:
                    timeline = utils.organize_by_blocks(experiment['timeline'],
                                                        experiment['count'],
                                                        bucket,
                                                        experiment['name'])
                    return render_template('experiment_html.html',
                                           title='Experiment',
                                           timeline=timeline,
                                           background_color=experiment['background_color'])
            except Exception as e:
                print("Error: " + str(e))
                continue
            finally:
                try_count += 1
        return render_template('experiment_does_not_exist.html',
                               title='Psychology Experiment')


@app.route('/export', methods=["GET", "POST"])
def export_experiment_result():
    if request.method == "POST":
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
    else:
        return render_template("export.html", title="Export")


@app.route('/upload_images', methods=["GET", "POST"])
def upload_images_to_experiment():
    if request.method == "POST":
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
                x = threading.Thread(target=utils.extract_and_upload_stimulus,
                                     args=(bucket, extract_folder, name,))
                x.start()

    return render_template("uploadImages.html", title="Add Stimulus")


@app.route('/details/<experiment_id>')
def get_experiment_detail(experiment_id):
    doc_ref = db.collection(u'Experiments').document(experiment_id)
    experiment = doc_ref.get().to_dict()
    return render_template("experiment_details.html", title="Details", lst=experiment['timeline'])


if __name__ == '__main__':
    app.run(debug=True)
