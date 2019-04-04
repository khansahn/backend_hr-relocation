from flask import Flask, request, abort, jsonify, make_response
import jwt

from src.routes import router
from src.utils.models import db

from flask_cors import CORS

app = Flask(__name__)   #buat manggil flask
app.register_blueprint(router)

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import exists

CORS(app)

POSTGRES = {
    'user' : 'postgres',
    'pw' : 'postgres',
    'db' : 'hrd',
    'host' : 'localhost',
    'port' : '3794'
}

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#postgresql: //username:password@localhost:3794/database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s'% POSTGRES

db.init_app(app)



@app.route('/addition/<int:firstNumber>/<int:secondNumber>')
def addition(firstNumber,secondNumber):
    response = {
        "data" : str(firstNumber + secondNumber),
        "message" : "berhasil"
    }
    return jsonify(response)

