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

