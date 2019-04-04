from flask import request, json, jsonify, g, abort
from functools import wraps

from .crypt import encrypt, decrypt
from .token import encode, decode

def generateToken(data):
    data = encrypt(data)
    token = encode(data)
    return token

def verifyLogin(f):
    @wraps(f)
    def decoratedFunction(*args, **kwargs):
        if "Authorization" not in request.headers:
            abort(403)
        # isTrue = False
        # if (isTrue) :
            # return "login gagal"
        # tokennya ditaro di headers dgn keyword "Bearer" spasi token makanya di bawah di-slice
        token = request.headers["Authorization"][7:]
        data = (decode(token))
        username = decrypt(data["data"])
        g.username = username
        return  f(*args, **kwargs)
    return decoratedFunction
