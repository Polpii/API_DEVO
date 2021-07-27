from os import stat
from flask import Flask, jsonify, request
from flask_restful import Api, Resource, reqparse, abort
import sqlite3

app = Flask(__name__)
api = Api(app)


# robots_list = [
#     {
#         "id"     : 0,
#         "name"   : "MK2R2_0",
#         "status" : 0,
#         "connection" : "ON"
#     },
#     {
#         "id"     : 1,
#         "name"   : "MK2R2_1",
#         "status" : 0
#         "connection" : "ON"
#     }
# ]

def db_connection():
    conn = None
    try:
        conn = sqlite3.connect("robots_sqlite.db", check_same_thread=False)
    except sqlite3.Error as e:
        print(e)
    return conn

conn = db_connection()
cur = conn.cursor()

def create_table():
    conn = sqlite3.connect("robots_sqlite.db")
    cur = conn.cursor()
    cur.execute("""CREATE TABLE robots(
        ID integer,
        name text,
        status text,
        connection text
    )""")

    conn.commit()

    conn.close()

def add_data_to_table(ID, name, status, connection):
    sql = """INSERT INTO robots VALUES (?, ?, ?, ?)"""
    cur.execute(sql, (ID, name, status, connection))
    
    conn.commit()
    # conn.close()

def add_column():
    conn = sqlite3.connect("robots_sqlite.db")
    cur = conn.cursor()
    cur.execute("""ALTER TABLE robots
                    ADD connection text""")

    conn.commit()

    conn.close()
    

# create_table()
# add_data_to_table(0, 'MK2R2_0', 'WORKING')
# add_column()


class GeneralRobot(Resource):
    def get(self):
        cursor = cur.execute("SELECT * FROM robots")

        robots = [
            dict(id=row[0], name=row[1], status=row[2], connection=row[3])
            for row in cursor.fetchall()
        ]

        if robots is not None:
            return jsonify(robots)

    # Create a new ROBOT in the Database
    def post(self):
        new_id = request.form['id']
        new_name = request.form['name']
        new_status = request.form['status']
        new_connection = request.form['connection']

        sql = """INSERT INTO robots (id, name, status, connection)
                VALUES (?, ?, ?, ?)"""

        cursor = cur.execute(sql, (new_id, new_name, new_status, new_connection))
        conn.commit()

        return f"Robot with the id: {cursor.lastrowid} created successfully"

class IdRobot(Resource):
    def get(self, id): 
        robot = None
        cursor = cur.execute("SELECT * FROM robots WHERE ID={}".format(id))
        rows = cursor.fetchall()

        robot = []

        for r in rows:
            robot.append(r)

        if robot is not None:
            return robot, 200
        else:
            abort(404, message="Something wrong")
        
    def put(self, id):
        sql = """ UPDATE robots 
                SET name=?, 
                    status=?,
                    connection=?
                WHERE id=? """
         
        name = request.form['name']
        status = request.form['status']
        connection = request.form['connection']


        updated_robot = {
            "id": id,
            "name": name,
            "status": status,
            "connection": connection
        }

        conn.execute(sql, (name, status, connection, id))
        conn.commit()
        return updated_robot
        

    def delete(self, id):
        sql = """ DELETE FROM robots WHERE id=? """
        conn.execute(sql, (id,))
        conn.commit()

        return "The book with id: {} has been deleted".format(id), 200

api.add_resource(GeneralRobot, '/robot', methods=['GET', 'POST'])
api.add_resource(IdRobot, '/robot/<int:id>', methods=['GET', 'PUT', 'DELETE'])



if __name__ == "__main__":
    app.run(debug=True)