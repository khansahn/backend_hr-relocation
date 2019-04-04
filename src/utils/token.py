import jwt
import os
from datetime import datetime, timedelta
from flask import jsonify, abort

def encode(data):
    payload = {
        "data" : data,
        "exp" : datetime.utcnow() + timedelta(seconds = 84600),
        "iat" : datetime.utcnow()
    }
    encoded = jwt.encode(payload,os.getenv("SECRET"),algorithm="HS256").decode('utf-8')
    return encoded

def decode(data):
    try:
        decoded = jwt.decode(data,os.getenv("SECRET"),algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        abort(403)
    except jwt.DecodeError:
        abort(403)
    return decoded