import flask
import sqlite3

from flask import request, jsonify, flash, redirect
from werkzeug.exceptions import HTTPException


app = flask.Flask(__name__)
app.config["DEBUG"] = True

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@app.route('/', methods=['GET'])
def home():
    return '''<h1>Distant DEVO</h1>
<p>API for distant reading of DEVO Robots Data.</p>'''


@app.route('/api/v1/resources/robots/all', methods=['GET'])
def api_all():
    conn = sqlite3.connect('robots.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    all_robots = cur.execute('SELECT * FROM robots;').fetchall()

    return jsonify(all_robots)



@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


@app.route('/api/v1/resources/robots', methods=['GET', 'POST'])
def api_filter():
    if request.method == 'GET':
        query_parameters = request.args


        allowed_parameters = ['id', 'volt', 'position', 'map', 'status']

        query = []
        query_objects = []
        for parameter, parameter_value in query_parameters.items():
            if parameter not in allowed_parameters:
                return  f'Parameter not allowed: {parameter}', 400

            query.append(f'{parameter}=?')
            query_objects.append(parameter_value)

        query = "SELECT * FROM robots WHERE " + ' AND '.join(query)

        # id = query_parameters.get('id')
        # volt = query_parameters.get('volt')
        # map = query_parameters.get('map')
        # position = query_parameters.get('position')
        # status = query_parameters.get('status')

        # query = "SELECT * FROM robots WHERE"
        # to_filter = []
        
        # if id:
        #     query += ' id=? AND'
        #     to_filter.append(id)
        # if volt:
        #     query += ' volt=? AND'
        #     to_filter.append(volt)
        # if map:
        #     query += ' map=? AND'
        #     to_filter.append(map)
        # if position:
        #     query += ' position=? AND'
        #     to_filter.append(position)
        # if status:
        #     query += ' status=? AND'
        #     to_filter.append(status)

        # if not (id or volt or map or position or status):
        #     return page_not_found(404)

        # query = query[:-4] + ';'

        conn = sqlite3.connect('robots.db')
        conn.row_factory = dict_factory
        cur = conn.cursor()

        results = cur.execute(query, query_objects).fetchall()

        return jsonify(results)
    
    if request.method == 'POST':
        #fetch form data
        productDetails = request.form
        #P_ID=productDetails['P_ID']
        id = productDetails['id']
        volt=100
        map= "{1,1,1,1,1,1,1}"
        position= "[100; 100]"
        status= "CHANGING"
        conn = sqlite3.connect('robots.db')
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        cursor.execute("UPDATE Robots SET volt=?, map=?, status=? WHERE id=?",(volt, map, status, id))
        conn.commit()
        cursor.close()
        # flash("Data Updated Successfully")
        # return redirect('/product')
        return {}


app.run(host="0.0.0.0")