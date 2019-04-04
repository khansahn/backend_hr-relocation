
from flask import Flask, request, json, jsonify, make_response
import os

from ..utils.crypt import encrypt, decrypt
from ..utils.authorisation import generateToken

from ..utils.models import db, Pegawai

from . import router

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import exists
from sqlalchemy import func




#####################################################################################################
# REGISTER USER
#####################################################################################################
@router.route('/user', methods=['POST'])
def registerUser():
    body = request.json

    body["password"] = encrypt(body["password"])

    nama = body["nama"]
    email = body["email"]
    password = body["password"]
    role_id = body["role_id"]
    posisi_id = body["posisi_id"]

    response = {
        "error" : True,
        "message" : "",
        "data" : {}
    }

    # cek email udah dipake belum
    emailExist = db.session.query(Pegawai).filter_by(email = email).scalar() is not None
    
    if (emailExist == True):
        response["message"] = "email is already exist"
    else:
        try:            
            pegawai = Pegawai(
                nama = nama,
                email = email,
                password = password,
                role_id = role_id,
                posisi_id = posisi_id,
                token_nf = None)

            db.session.add(pegawai)
            db.session.commit()

            response["message"] =  "Pegawai created. Pegawai-npk = {}".format(pegawai.npk)
            response["error"] = False
            response["data"] = pegawai.returnToUser()
        except Exception as e:
            response["message"] = str(e)
        finally:
            db.session.close()

    
    return jsonify(response)




#####################################################################################################
# LOGIN USER
#####################################################################################################
@router.route('/user/login', methods = ['POST'])
def loginUser():
    body = request.json

    response = {
        "error" : True,
        "message" : "",
        "data" : {}
    }
    errorCode = 404

    # cek username ada atau engga
    emailExist = db.session.query(Pegawai).filter_by(email = body["email"]).scalar() is not None

    if (emailExist == True) :
        try:
            pegawai = db.session.query(Pegawai).filter_by(email = body["email"]).first()
            pegawai.serialise()
            if (decrypt(pegawai.password) == body["password"]):
                data = {
                    # ini tokennya generate pake nama, ga unik.
                    "token" : generateToken(pegawai.nama.lower()),
                    "nama" : pegawai.nama,
                    "npk" : pegawai.npk
                }
                response["message"] = "Login berhasil"
                response["error"] = False
                response["data"] = data
                errorCode = 200
            else:
                response["message"] = "Incorrect gov eh pass"
                errorCode = 401

        except Exception as e:
            response["message"] = str(e)

        finally:
            db.session.close()

    else:
        response["message"] = "Email is not registered"
        errorCode = 401
    return jsonify(response), errorCode

#####################################################################################################
# GET USER PER ID
#####################################################################################################
@router.route('/user/getUser/<npk>')
def getUserById(npk):
    response = {
        "error" : True,
        "message" : "",
        "data" : {}
    }

    # cek username ada atau engga
    pegawaiExist = db.session.query(Pegawai).filter_by(npk = npk).scalar() is not None

    if (pegawaiExist == True) :
        try:
            pegawai = Pegawai.query.filter_by(npk = npk).first()

            response["message"] ="User found"
            response["error"] = False
            response["data"] = (pegawai.returnToUser())
        except Exception as e:
            response["message"] = str(e)
        finally:
            db.session.close()

    else :
        response["message"] = "Pegawai is not found"

    return jsonify(response)



#####################################################################################################
# GET DETAIL POSISI PER PEGAWAI NPK
#####################################################################################################
@router.route('/user/getDetailedPosisi/<npk>')
def getDetailedPosisiById(npk):
    response = {
        "error" : True,
        "message" : "",
        "data" : {}
    }

    # cek username ada atau engga
    pegawaiExist = db.session.query(Pegawai).filter_by(npk = npk).scalar() is not None

    if (pegawaiExist == True) :
        try:
            pegawai = Pegawai.query.filter_by(npk = npk).first()

            response["message"] ="User found"
            response["error"] = False
            response["data"] = (pegawai.getDetailedPosisiOnPegawaiAtNPK())
        except Exception as e:
            response["message"] = str(e)
        finally:
            db.session.close()

    else :
        response["message"] = "Pegawai is not found"

    return jsonify(response)


#####################################################################################################
# GET ALL USERS
#####################################################################################################
@router.route('/user/getAll')
def getAllUsers():
    response = {
        "error" : True,
        "message" : "",
        "data" : {}
    }

    try:
        pegawaiEnabled = Pegawai.query.filter_by(status_enabled = True).order_by(Pegawai.nama).all()

        data = ([e.returnToUser() for e in pegawaiEnabled])
        pegawaiEnabledCount  = len(data)
        response["message"] = "Pegawai(s) found : " + str(pegawaiEnabledCount)
        response["error"] = False
        response["data"] = data
    except Exception as e:
        response["message"] = str(e)
    finally:
        db.session.close()


    return jsonify(response)

