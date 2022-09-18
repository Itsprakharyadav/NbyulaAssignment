from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from pymongo import MongoClient
import os
import jwt

database_url = os.environ['DB_URL']
database_name = os.environ['DB_NAME']

client = MongoClient(database_url)
database = client.get_database(database_name)
collection = database["users"]

app = Flask(__name__)
api = Api(app)

class Landing(Resource):

    def get(self):
        # print("Connected to the MongoDB database!")
        # user = {'username': 'test', 'password' : 'test'}
        # print(collection.count_documents({}))
        # collection.insert_one(user)
        return jsonify({'Message': 'Landing Page'})

lass Login(Resource):

    def get(self):
        email = request.json['email']
        password = request.json['password']

        email_exist_check = collection.find_one({'email': email})

        if email_exist_check:
            if email_exist_check['password'] == password:
                token = jwt.encode({"username": email_exist_check['username']},
                                   "vader",
                                   algorithm="HS256")
                return jsonify({"message": "Logged In", "token": token})
        else:
            return jsonify({"message": "Invalid email or password"})

