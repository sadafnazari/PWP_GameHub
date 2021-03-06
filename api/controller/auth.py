from flask import (
    Blueprint, request, jsonify
)

from werkzeug.exceptions import (BadRequest)

from jsonschema import validate, ValidationError

from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required

from api.db import check_login
from api.db import add_user

from api.models import User

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["POST"])
def login():
    """
    Login endpoint.
    --- 
    consumes:
    - "application/json"
    produces:
    - "application/json"
    parameters:
    - name: body
      in: body
      required: true
      description: "Login data"
      schema: 
        id: login_schema
        required:
        - username
        - password
        properties:
          username:
            type: string
            example: "test"
          password:
            type: string
            example: "1234"
            
    responses:
        200:
            description: login success
            schema:
              type: object
              properties:
                access_token: 
                    type: string
                    example: "A Valid Token"
                status:
                    type: string
                    example: "success"
                payload:
                    type: object
                    properties:
                        username:
                            type: string
                            example: "test"
                        email:
                            type: string
                            example: "test@test.com"
                        id:
                            type: integer
                            example: 1
        400:
            description: schema validation failed
        
        401:
            description: login failed
            schema:
                type: object
                properties:
                    status:
                        type: string
                        example: "fail"
    """
    response = {"status": "",
                "payload": {},
                "access_token": ""}

    # if all(k in request.form.keys() for k in ["username",
    #                                             "password"]):
    try:
        validate(instance=request.json, schema=User.login_json_schema())
        res = check_login(request.json['username'].lower(), request.json['password'])
        if res[0] != "ok":
            response["status"] = res[0]
            return jsonify(response), 401
        
        token = create_access_token(identity=res[1].__dict__)
        response["status"] = res[0]
        response["payload"] = res[1].__dict__
        response["access_token"] = token
        return jsonify(response), 200
    # else:
    except ValidationError as e:
        raise BadRequest(description=str(e))


@bp.route("/signup", methods = ["POST"])
def addUser():
    """
    signup endpoint.
    ---
    consumes:
    - "application/json"
    produces:
    - "application/json"
    parameters:
    - name: body
      in: body
      required: true
      description: "Signup data"
      schema:
        id: signup_schema
        required:
        - username
        - password
        - email
        properties:
            username:
                type: string
                example: "test"
            password:
                type: string
                example: "1234"
            email:
                type: string
                example: "test@test.com"
    responses:
        201:
            description: signup success
            schema:
                type: object
                properties:
                    status:
                        type: string
                        example: "success"
        400:
            description: schema validation failed or username already exists
    """
    response = {"status": "",
                "payload": {},
                "access_token": ""}

    # if all(k in request.form.keys() for k in ["username",
    #                                           "password",
    #                                           "email",
    #                                           ]):
    try:
        
        validate(instance=request.json, schema=User.signup_json_schema())
        if (request.json['username'].strip() == "" or 
            request.json['password'].strip() == "" or 
            "@" not in request.json["email"]):
            
            response["status"] = "invalid"
            return jsonify(response), 400
            
        res = add_user(request.json['username'].lower(),
                       request.json['password'],
                       request.json["email"],
                       request.json["avatar"] if "avatar" in request.json.keys() else None
                       )

        if res != "ok":
            response["status"] = res
            return jsonify(response), 400
        
        else:
            response["status"] = "ok"
            return jsonify(response), 201
    # else:
    except ValidationError as e:
        raise BadRequest(description=str(e))


@bp.route("/token_test", methods=["GET"])
@jwt_required()
def token_test():
    """
    Test endpoint to check if the access token is valid
    Authorization header must be set to the access token
    :paramters:
        None
    :headers:
        Authorization: Bearer <access_token>
    :return:   json

    """
    response = {"status": "",
                "payload": {},
                }
    response["status"] = "ok"
    return jsonify(response), 200
