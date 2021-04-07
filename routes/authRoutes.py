import os

from flask import request, jsonify
from flask_jwt_extended import create_access_token
from flask_restful import Resource
from pymongo import MongoClient

from constants import Errors, Messages, EnvironmentVariables, DBTables
from dataHandler import DataHandler


class Register(Resource):
    def post(self):
        email = request.form["email"]
        test = DataHandler().find_user_by_email(email)
        if test:
            return jsonify(message=Errors.AuthenticationErrors.UserAlreadyExist), 409
        else:
            user_name = request.form["user_name"]
            password = request.form["password"]
            user_info = dict(user_name=user_name, email=email, password=password)
            user.insert_one(user_info)
            return jsonify(message=Messages.UserAddedSuccessfully), 201


class Login(Resource):
    def post(self):
        if request.is_json:
            email = request.json["email"]
            password = request.json["password"]
        else:
            email = request.form["email"]
            password = request.form["password"]

        test = user.find_one({"email": email, "password": password})
        if test:
            access_token = create_access_token(identity=email)
            return jsonify(message=Messages.LoginSucceeded, access_token=access_token), 201
        else:
            return jsonify(message=Errors.AuthenticationErrors.BadEmailOrPassword), 401
