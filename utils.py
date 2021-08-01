from flask import request
from flask import session


def check_session():
    session_id = request.args.get('session_id')
    name = session.get(session_id)
    return name

