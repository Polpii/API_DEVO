from flask import Flask, jsonify
from werkzeug.exceptions import abort
from flask_restful import Api, Resource, reqparse, abort
import sqlite3

app = Flask(__name__)
api = Api(app)

names = {"Teddy": {"age": 23, "gender": "male", "activate": "yes"},
        "Thomas": {"age": 23, "gender": "male", "activate": "no"}}

map_number = 0;
map = {"Number": map_number}

robot_put_args = reqparse.RequestParser()
robot_put_args.add_argument("name", type=str, help="Name of the robot")
# robot_put_args.add_argument("battery", type=int, help="Get the battery voltage of the robot")


robots = {"MK2R2_id": [
            {0: 
                {
                    "name" : "MK2R2_0",
                    "Data" : 
                    {
                        "ultrasonic" :
                        {
                            "FR"  : "100",
                            "FMR" : "155",
                            "FML" : "20",
                            "FL"  : "300"
                        }, 
                        "battery": 8
                    }
                }
            },
            {1: 
                {
                    "name" : "MK2R2_1",
                    "Data" : 
                    {
                        "ultrasonic" :
                        {
                            "FR"  : "0",
                            "FMR" : "0",
                            "FML" : "0",
                            "FL"  : "0"
                        }, 
                        "battery": 8
                    }
                }
            }
        ]
    }

def abort_if_robot_not_known(id):
    if id not in robots["MK2R2_id"]:
        abort(404, message="This robot id doesn't exist...")

def abort_if_robot_exists(id):
    if id in robots:
        abort(409, message="This robot id already exists with that id...")

class HelloWorld(Resource):
    def get(self, name):
        return names[name]

    def post(self):
        return {"data": "Posted"}

class CheckMap(Resource):
    def get(self):
        return map

class Robot(Resource):
    def get(self, id):
        # abort_if_robot_not_known(id)
        return robots["MK2R2_id"][id]

    def put(self, id):
        args = robot_put_args.parse_args()
        robots["MK2R2_id"][id] = args
        return robots["MK2R2_id"][id], 201

    def delete(self, id):
        # abort_if_robot_exists(id)
        del robots["MK2R2_id"][id]
        return '', 204



api.add_resource(HelloWorld, "/helloworld/<string:name>")
api.add_resource(CheckMap,   "/checkmap")
api.add_resource(Robot,      "/robot/<int:id>")

if __name__ == "__main__":
    app.run(debug=True)