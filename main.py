# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import json

from flask import Flask
from flask import session
from flask import g
from flask import request
import dbaccess
import uuid
import os
from utils import check_session

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'pg_conn'):
        dbaccess.disconnect_db(g.pg_conn)


@app.route('/')
def index():
    return 'hello world'


@app.route('/getcustomer')
def get_customers():
    sql = "select * from customer;"
    rows = dbaccess.select_table(sql)

    rows_str = json.dumps(rows)
    return rows_str


@app.route('/register')
def register():
    result = {}

    name = request.args.get('name')
    pwd = request.args.get('pwd')

    row = {'name': "'%s'" % name, 'pwd': "'%s'" % pwd}
    ret = dbaccess.insert_table('customer', row)
    if ret:
        result['ret'] = 'success'
    else:
        result['ret'] = 'failed'
        result['error'] = 'insert customer failed'

    return result


@app.route('/login')
def login():
    session.permanent = True

    name = request.args.get('name')
    pwd = request.args.get('pwd')

    sql = "select * from customer where name = '%s' and pwd = '%s'" % (name, pwd)
    rows = dbaccess.select_table(sql)
    session_id = uuid.uuid1()
    session[str(session_id)] = name

    result = {}

    if len(rows) == 1:
        result['ret'] = 'success'
        result['session_id'] = str(session_id)
        return result
    else:
        result['ret'] = 'failed'
        return result


@app.route('/postevent')
def post_event():
    result = {}
    name = check_session()
    if name is None:
        result['ret'] = 'failed'
        result['error'] = 'session timeout'
        return result

    x = request.args.get('x')
    y = request.args.get('y')
    event_name = request.args.get('name')

    row = {'x': x, 'y': y, 'name': "'%s'" % event_name, 'customer_name': "'%s'" % name}

    ret = dbaccess.insert_table('event', row)

    if not ret:
        result['ret'] = 'failed'
        result['error'] = 'insert event failed'
    else:
        result['ret'] = 'success'
    return result

@app.route('/getevent')
def get_event():
    result = {}
    name = check_session()
    if name is None:
        result['ret'] = 'failed'
        result['error'] = 'session timeout'
        return result
    x1 = request.args.get('x1')
    y1 = request.args.get('y1')
    x2 = request.args.get('x2')
    y2 = request.args.get('y2')

    columns = ["id", "x", "y", "name", "customer_name"]

    sql = "select * from event where x >= %s and x <= %s and y >= %s and y <= %s" % (x1, x2, y1, y2)
    rows = dbaccess.select_table(sql)
    if len(rows) >= 1:
        result['ret'] = 'success'

        events = []
        for row in rows:
            event = {}
            for i in range(len(row)):
                event[columns[i]] = row[i]

            events.append(event)

        result['events'] = events
    else:
        result['ret'] = 'failed'

    return result


@app.route('/postcomment')
def post_comment():
    result = {}
    name = check_session()
    if name is None:
        result['ret'] = 'failed'
        result['error'] = 'session timeout'
        return result

    event_id = request.args.get('event_id')
    content = request.args.get('content')

    row = {'event_id': event_id, 'content': "'%s'" % content, 'customer_name': "'%s'" % name}
    ret = dbaccess.insert_table('comment', row)
    if not ret:
        result['ret'] = 'failed'
        result['error'] = 'insert comment failed'
    else:
        result['ret'] = 'success'
    return result


@app.route('/getcomment')
def get_comment():
    result = {}
    name = check_session()
    if name is None:
        result['ret'] = 'failed'
        result['error'] = 'session timeout'
        return result

    event_id = request.args.get('event_id')
    sql = "select * from comment where event_id = %s" % event_id
    rows = dbaccess.select_table(sql)
    columns = ["id", "event_id", "content", "customer_name"]
    if len(rows) >= 1:
        result['ret'] = 'success'
        comments = []
        for row in rows:
            comment = {}
            for i in range(len(row)):
                comment[columns[i]] = row[i]

            comments.append(comment)

        result['comments'] = comments
    else:
        result['ret'] = 'failed'

    return result


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8090)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
