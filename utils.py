import datetime
import json
import os
import random
from copy import deepcopy
from itertools import permutations

import pandas as pd
from flask import make_response, jsonify

from constants import Errors, PluginNames, BrmsTypes, BrmsProperties
from handlers.dataHandler import DataHandler
from handlers.storageHandler import StorageHandler


def create_response(response_content, response_status):
    response = make_response(jsonify(response_content), response_status)
    response.headers["Content-Type"] = "application/json"
    return response


def brms_exist(timeline):
    for trial in timeline:
        if trial.type == PluginNames.bRMS:
            return True
    return False


def get_random_group(groups):
    random_group = random.choice(groups)
    new_group = []
    other_sub_groups = []
    for item in groups[random_group]:
        sub_group = 0
        if BrmsProperties.SubGroup in item:
            sub_group = int(item[BrmsProperties.SubGroup])
        if sub_group == 0:
            new_group.append(item)
        else:
            new_group.append(None)
            if sub_group in other_sub_groups:
                other_sub_groups[sub_group].append(item)
            else:
                other_sub_groups[sub_group] = [item]

    result = []
    for item in new_group:
        if item is not None:
            result.append(item)
        else:
            random_sub_group = random.choice(other_sub_groups)
            result.append(random_sub_group)
            other_sub_groups.remove(random_sub_group)
    return result


def get_mixed_value_list(dic):
    result = []
    for item in dic:
        for list_item in dic[item]:
            result.append((item, list_item))
    current_list = shuffle_list(result)
    return current_list


def get_random_value_list(dic):
    result = []
    keys = shuffle_list(dic.keys())
    for item in keys:
        for list_item in dic[item]:
            result.append((item, list_item))
    return result


def get_ordered_value_list(dic):
    result = []
    for item in dic:
        for list_item in dic[item]:
            result.append((item, list_item))
    return result


def shuffle_list(lst):
    new_list = deepcopy(lst)
    # using Fisher Yates shuffle Algorithm
    # to shuffle a list
    for i in range(len(new_list) - 1, 0, -1):
        # Pick a random index from 0 to i
        j = random.randint(0, i)
        # Swap arr[i] with the element at random index
        new_list[i], new_list[j] = new_list[j], new_list[i]
    return new_list


def order_brms(trial, experiment_name, count):
    new_brms = []
    stimulus_dictionary = trial[BrmsProperties.StimulusDictionary]
    if trial[BrmsProperties.BrmsType] == BrmsTypes.Mix:
        values_list = get_mixed_value_list(stimulus_dictionary)
        new_brms.extend(add_brms_from_list(trial, values_list, experiment_name, count))
    elif trial[BrmsProperties.BrmsType] == BrmsTypes.Random:
        values_list = get_random_group(stimulus_dictionary)
        new_brms.extend(add_brms_from_list(trial, values_list, experiment_name, count))
    else:
        value_list = get_ordered_value_list(stimulus_dictionary)
        new_brms.extend(add_brms_from_list(trial, value_list, experiment_name, count))
    return new_brms


def add_brms_from_list(trial, values_list, experiment_name, count):
    all_trials = []
    for stimulus in values_list:
        trial_copy = deepcopy(trial)
        trial_copy[BrmsProperties.StimulusBlock] = stimulus[0]
        trial_copy[BrmsProperties.Count] = count
        trial_copy[BrmsProperties.File] = os.path.basename(stimulus[1])
        image_blob = StorageHandler().get_image_blob(experiment_name + "/" + trial_copy[BrmsProperties.File])
        trial_copy[BrmsProperties.Stimulus] = image_blob.generate_signed_url(datetime.timedelta(seconds=300),
                                                                             method='GET')
        trial_copy["stimulus_dictionary"] = None
        all_trials.append(trial_copy)
    return all_trials


def set_image_trials(trial):
    trial_copy = deepcopy(trial)
    trial_copy[BrmsProperties.Stimulus] = "data:image/jpeg;base64," + trial[BrmsProperties.Stimulus]
    return trial_copy


def get_all_seq(lst):
    return list(permutations(lst, len(lst)))


def organize_by_blocks(timeline, count, experiment_name):
    result_timeline = []
    block_division = {}
    try:
        for item in timeline:
            if item[BrmsProperties.Block] == 0:
                result_timeline.append(item)
            else:
                if str(item[BrmsProperties.Block]) in block_division.keys():
                    block_division[str(item[BrmsProperties.Block])].append(item)
                else:
                    block_division[str(item[BrmsProperties.Block])] = [item]

                if str(item[BrmsProperties.Block]) not in result_timeline:
                    result_timeline.append(str(item[BrmsProperties.Block]))
    except Exception:
        raise Exception("Block order error")

    all_seq = get_all_seq(list(block_division.keys()))
    current_seq = all_seq[count % len(all_seq)]
    new_timeline = order_sub_blocks(block_division, current_seq, result_timeline)
    final_timeline = []

    for item in new_timeline:
        if item[BrmsProperties.Type] == PluginNames.bRMS:
            new_brms = order_brms(item, experiment_name, count)
            for brms_item in new_brms:
                final_timeline.append(brms_item)
        elif item[BrmsProperties.Type] == PluginNames.ImageButton or \
                item[BrmsProperties.Type] == "":
            final_timeline.append(set_image_trials(item))
        else:
            final_timeline.append(item)

    return final_timeline


def order_sub_blocks(block_division, current_seq, timeline):
    """
    Order sub blocks
    :param block_division:
    :param current_seq:
    :param timeline:
    :return:
    """
    final_timeline = []
    loop_timeline = deepcopy(timeline)
    count = 0
    for item in loop_timeline:
        if isinstance(item, str):
            current_block = block_division[current_seq[count]]
            del block_division[current_seq[count]]
            count += 1
            sub_blocks = {}
            current_block_timeline = []
            for trial in current_block:
                if trial[BrmsProperties.SubGroup] == 0:
                    current_block_timeline.append(trial)
                else:
                    if str(trial[BrmsProperties.SubGroup]) in sub_blocks.keys():
                        sub_blocks[str(trial[BrmsProperties.SubGroup])].append(trial)
                    else:
                        sub_blocks[str(trial[BrmsProperties.SubGroup])] = [trial]
                    current_block_timeline.append(str(trial[BrmsProperties.SubGroup]))
            for trial in current_block_timeline:
                if isinstance(trial, str):
                    current_trial = random.choice(sub_blocks[trial])
                    final_timeline.append(current_trial)
                    del sub_blocks[trial][sub_blocks[trial].index(current_trial)]
                else:
                    final_timeline.append(trial)
        else:
            final_timeline.append(item)
    return final_timeline


def collection_to_csv(collection):
    """
    Upload collection value to CSV file
    :param collection: Collection
    :return: None
    """
    final_df = pd.DataFrame()
    try:
        dict4json = []
        n_documents = 0
        for document in collection.get():
            result_dict = document.to_dict()
            dict4json.append(result_dict)
            n_documents += 1
        for result in dict4json:
            lst = result["result"]
            df = pd.DataFrame(lst)
            df = df.reindex(sorted(df.columns), axis=1)
            final_df = pd.concat([final_df, df])
    except Exception as e:
        print(e)
        return pd.DataFrame()
    finally:
        return final_df


def delete_collection(coll_ref, batch_size):
    """
    Delete collection
    :param coll_ref: collection reference
    :param batch_size: collection size
    """
    docs = coll_ref.limit(batch_size).stream()
    deleted = 0

    for doc in docs:
        print(u'Deleting doc {} => {}'.format(doc.id, doc.to_dict()))
        doc.reference.delete()
        deleted = deleted + 1

    if deleted >= batch_size:
        return delete_collection(coll_ref, batch_size)


def get_collection_count(coll_ref_stream):
    """
    Get collection documents count
    :param coll_ref_stream: collection reference stream
    :return: collection documents count
    """
    count = 0
    for _ in coll_ref_stream:
        count += 1
    return count


def handle_input(experiment_file, uid):
    """
    Handle experiment.py file input
    :param experiment_file:  experiment.py file (json)
    :param uid:  user id
    :return: result and error message
    """
    result = ''
    error_msg = ''
    try:
        upload_experiment(experiment_file, uid)
    except Exception as e:
        error_msg = Errors.LOAD_EXPERIMENT_ERROR
        print(e)

    return result, error_msg


def upload_data(data_dic, name):
    """
    Upload trial result
    :param data_dic: Result dictionary
    :param name: experiment.py name
    :return: None
    """
    try:
        DataHandler().upload_data(name, data_dic)
    except Exception as e:
        print('Failed to upload to ftp: ' + str(e))


def upload_experiment(experiment_file, uid):
    """
    Upload experiment.py
    :param experiment_file:  Experiment file
    :param uid: User Id
    :return:
    """
    parsed_json = json.load(experiment_file)
    parsed_json["uid"] = uid
    parsed_json["count"] = 0
    try:
        DataHandler().upload_experiment(parsed_json)
    except Exception as e:
        print('Failed to upload to ftp: ' + str(e))


def extract_and_upload_stimulus(extract_folder, name):
    for file_name in os.listdir(extract_folder):
        try:
            extension = os.path.splitext(file_name)[1]
            if extension in ['.jpg', '.jpeg', '.png']:
                done = False
                try_count = 0
                while not done and try_count < 5:
                    try:
                        image_blob = StorageHandler().get_image_blob(name + "/" + file_name)
                        image_blob.upload_from_filename(extract_folder + file_name)
                        done = True
                        os.remove(extract_folder + file_name)
                        if try_count > 0:
                            print("Try " + str(try_count + 1) + " : worked!")
                    except Exception as exp:
                        print("Try " + str(try_count + 1) + " : " + str(exp))
                        try_count += 1
        except Exception as e:
            print(e)


def delete_stimulus_folder(experiment_name):
    try:
        StorageHandler().delete_stimulus_of_experiment(experiment_name)
    except Exception as e:
        print("Error on delete " + experiment_name + str(e))
