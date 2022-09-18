from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from pymongo import MongoClient
import os
import jwt

def overlap_check(time, potential_new_appointment_time):
    if potential_new_appointment_time[0] > time[0] and potential_new_appointment_time[1] < time[1]:
      return True
    else:
      return False


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

class Schedule(Resource):

    def put(self):
        token = request.json['token']
        username = jwt.decode(token, "vader", algorithms=["HS256"])['username']

        title = request.json['title']
        agenda = request.json['agenda']
        time = request.json['time']
        guest = request.json['guest']

        if username == guest:
            return jsonify({"message": "Cannot be Scheduled"})

        username_exist_check = collection.find_one({'username': username})
        guest_exist_check = collection.find_one({'username': guest})

        if username_exist_check and guest_exist_check:
            host_appointments = username_exist_check['appointments']
            guest_appointments = guest_exist_check['appointments']

            host_available = True
            guest_available = True

            for appointment in host_appointments:
                if overlap_check(appointment['time'], time):
                    # host_appointments.append(Appointment(tile, agenda, time, guest))
                    host_available = False

            for appointment in guest_appointments:
                if overlap_check(appointment['time'], time):
                    guest_available = False

            if host_available and guest_available:
                host_appointments.append(
                    {'title': title, 'agenda': agenda, 'time': time, 'guest': guest})
                guest_appointments.append(
                    {'title': title, 'agenda': agenda, 'time': time, 'guest': guest})

            print(host_appointments)

            host_query = {'username': username}
            guest_query = {'username': guest}

            update_host = {"$set": {'appointments': host_appointments}}
            update_guest = {"$set": {'appointments': guest_appointments}}

            print('Here')

            collection.update_one(host_query, update_host)
            collection.update_one(guest_query, update_guest)

            return jsonify({'message': f'Appointment scheduled for {time}'})

        else:
            return jsonify({"message": "Something went wronng"})

    def get(self):
        token = request.json['token']
        username = jwt.decode(token, "vader", algorithms=["HS256"])['username']
        # print(username)

        username_exist_check = collection.find_one({'username': username})

        if username_exist_check:
            if len(username_exist_check['appointments']) < 1:
                return jsonify({"message": "No Appointments"})
            else:
                return jsonify(
                    {"Appointments": username_exist_check['appointments']})
        else:
            return jsonify({"message": "Something went wrong"})


class MarkOff(Resource):

    def put(self):
        token = request.json['token']
        username = jwt.decode(token, "vader", algorithms=["HS256"])['username']
        time = request.json['time']

        username_exist_check = collection.find_one({'username': username})
        # print(username_exist_check)

        if username_exist_check:
            appointments = username_exist_check['appointments']

            for appointment in appointments:
                if appointment.overlap_check(time):
                    return jsonify({'message': 'cannot be marked as off'})

            appointments.append({'title': 'Off', 'agenda': 'off', 'time': time, 'guest': ''})
            query = {'username': username}
            update_appointments = {"$set": {'appointments': appointments}}
            collection.update_one(query, update_appointments)

            return jsonify({'message': f'Off Hours marked for {time}'})
        else:
            return jsonify({'message': 'Something went wrong'})


class ChangeNameAndPassword(Resource):

    def put(self):
        token = request.json['token']
        username = jwt.decode(token, "vader", algorithms=["HS256"])['username']

        username_exist_check = collection.find_one({'username': username})

        new_username = request.json['new_username']
        new_password = request.json['new_password']

        # print(username_exist_check)

        if username_exist_check:

            if new_password:
                query = {'username': username}
                update_password = {"$set": {'password': new_password}}
                collection.update_one(query, update_password)

            elif new_username:
                query = {'username': username}
                update_username = {"$set": {'username': new_username}}
                collection.update_one(query, update_username)

            else:
                return jsonify({'message': 'No Updates'})

            return jsonify({'message': 'Credentials updated'})

        else:
            return jsonify({'message': 'Something went wrong'})

api.add_resource(Landing, '/')
api.add_resource(Signup, '/signup')
api.add_resource(Login, '/login')
api.add_resource(Schedule, '/schedule')
api.add_resource(MarkOff, '/offhours')
api.add_resource(ChangeNameAndPassword, '/change')

if __name__ == '__main__':
    app.run(debug=True)
