import datetime

from flask import request
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_restful import Resource
from mongoengine.errors import FieldDoesNotExist, NotUniqueError, DoesNotExist

from assets.errors import SchemaValidationError, EmailAlreadyExistsError, UnauthorizedError, \
    InternalServerError
from database.user import User


class SignupApi(Resource):
    def post(self):
        try:
            email = request.form["email"]
            password = request.form["password"]
            user = User(email=email, password=password)
            print(user)
            user.hash_password()
            user.save()
            id = user.id
            return {'id': str(id)}, 200
        except FieldDoesNotExist:
            raise SchemaValidationError
        except NotUniqueError:
            raise EmailAlreadyExistsError
        except Exception as e:
            raise InternalServerError


class LoginApi(Resource):
    def post(self):
        try:
            user = User.objects.get(email=request.form.get('email'))
            authorized = user.check_password(request.form.get('password'))
            if not authorized:
                raise UnauthorizedError

            expires = datetime.timedelta(days=7)
            access_token = create_access_token(identity=str(user.id), expires_delta=expires)
            refresh_token = create_refresh_token(identity=str(user.id))
            return {'access_token': access_token, 'refresh_token': refresh_token}, 200
        except (UnauthorizedError, DoesNotExist):
            raise UnauthorizedError
        except Exception:
            raise InternalServerError
