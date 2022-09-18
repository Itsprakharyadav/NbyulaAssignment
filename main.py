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

class Signup(Resource):

    def post(self):
        username = request.json['username']
        email = request.json['email']
        password = request.json['password']

        # print(username, email, password)

        email_exist_check = collection.find_one({'email': email})
        username_exist_check = collection.find_one({'username': username})

        if email_exist_check or username_exist_check:
            return jsonify({"message": "Username or Email already exist"})
        else:
            collection.insert_one({
                'username': username,
                'email': email,
                'password': password,
                "appointments": []
            })
            return jsonify({"message": "User added succesfully"})

class Signup(Resource):
  pass

class Schedule(Resource):
  pass

class MarkOff(Resource):
  pass

class ChangeNameAndPassword(Resource):
  pass

api.add_resource(Landing, '/')
api.add_resource(Signup, '/signup')
api.add_resource(Login, '/login')
api.add_resource(Schedule, '/schedule')
api.add_resource(MarkOff, '/offhours')
api.add_resource(ChangeNameAndPassword, '/change')

if __name__ == '__main__':
    app.run(debug=True)
