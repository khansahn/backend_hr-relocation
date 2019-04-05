
from flask import Flask, request, json, jsonify, make_response
import os

from ..utils.models import db, Posisi, Role, Keputusan
from ..utils.authorisation import verifyLogin


from . import router

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import exists
from sqlalchemy import func


#####################################################################################################
# ADD ROLE
#####################################################################################################
@router.route('/master/role/add', methods=['POST'])
def addRole():
    body = request.json

    role_name = body["role_name"]
    posisi_id = body["posisi_id"]
    # status_enabled = body["status_enabled"]

    response = {
        "error" : True,
        "message" : "",
        "data" : {}
    }

    try:            
        role = Role(
            role_name = role_name,
            posisi_id = posisi_id)
            # status_enabled = status_enabled)

        db.session.add(role)
        db.session.commit()

        response["message"] =  "Role created. Role-id = {}".format(role.role_id)
        response["error"] = False
        response["data"] = role.serialise()
    except Exception as e:
        response["message"] = str(e)
    finally:
        db.session.close()
    
    return jsonify(response)


#################################################################################################
# GET ROLE
#################################################################################################
@router.route('/master/role/getAll', methods=['GET'])

def getAllRole():
    response = {
        "error" : True,
        "message" : "",
        "data" : {}
    }
    
    try:
        roleEnabled = Role.query.filter_by(status_enabled = True).order_by(Role.role_id).all()

        data = ([e.serialise() for e in roleEnabled])
        roleEnabledCount  = len(data)
        response["message"] = "Role(s) found : " + str(roleEnabledCount)
        response["error"] = False
        response["data"] = data
    except Exception as e:
        response["message"] = str(e)
    finally:
        db.session.close()

    
    return jsonify(response)




#################################################################################################
# GET ROLE PER ID POSISI
#################################################################################################
@router.route('/master/role/getRoleByPosisiId/<posisi_id>', methods=['GET'])
@verifyLogin

def getRoleByPosisiId(posisi_id):
    response = {
        "error" : True,
        "message" : "",
        "data" : {}
    }
    
    try:
        role = Role.query.filter_by(status_enabled = True, posisi_id = posisi_id ).order_by(Role.role_name).all()

        data = [e.serialise() for e in role]
        response["message"] = "Role(s) found"
        response["error"] = False
        response["data"] = data
    except Exception as e:
        response["message"] = str(e)
    finally:
        db.session.close()

    
    return jsonify(response)




#################################################################################################
# GET ROLE MANAJER PER ID POSISI
#################################################################################################
@router.route('/master/role/getRoleManajerByPosisiId/<posisi_id>', methods=['GET'])
@verifyLogin

def getRoleManajerByPosisiId(posisi_id):
    response = {
        "error" : True,
        "message" : "",
        "data" : {}
    }
    
    try:
        role = Role.query.filter_by(status_enabled = True, posisi_id = posisi_id,role_name = "Manajer").order_by(Role.role_name).first()

        # data = [e.serialise() for e in role]
        response["message"] = "Role manajer found"
        response["error"] = False
        response["data"] = role.serialise()
    except Exception as e:
        response["message"] = str(e)
    finally:
        db.session.close()

    
    return jsonify(response)


#####################################################################################################
# ADD POSISI
#####################################################################################################
@router.route('/master/posisi/add', methods=['POST'])
@verifyLogin

def addPosisi():
    body = request.json

    posisi_name = body["posisi_name"]
    posisi_type = body["posisi_type"]
    area = body["area"]
    company = body["company"]

    # status_enabled = body["status_enabled"]  

    response = {
        "error" : True,
        "message" : "",
        "data" : {}
    }

    try:            
        posisi = Posisi(
            posisi_name = posisi_name,
            posisi_type = posisi_type,
            area = area,
            company = company)
            # status_enabled = status_enabled)

        db.session.add(posisi)
        db.session.commit()

        response["message"] =  "Posisi created. Posisi-id = {}".format(posisi.posisi_id)
        response["error"] = False
        response["data"] = posisi.serialise()
    except Exception as e:
        response["message"] = str(e)
    finally:
        db.session.close()
    
    return jsonify(response)



#################################################################################################
# GET POSISI
#################################################################################################
@router.route('/master/posisi/getAll', methods=['GET'])
def getAllPosisi():
    response = {
        "error" : True,
        "message" : "",
        "data" : {}
    }
    
    try:
        posisiEnabled = Posisi.query.filter_by(status_enabled = True).order_by(Posisi.posisi_id).all()

        data = ([e.serialise() for e in posisiEnabled])
        posisiEnabledCount  = len(data)
        response["message"] = "Posisi(s) found : " + str(posisiEnabledCount)
        response["error"] = False
        response["data"] = data
    except Exception as e:
        response["message"] = str(e)
    finally:
        db.session.close()

    
    return jsonify(response)




#################################################################################################
# GET POSISI PER ID POSISI
#################################################################################################
@router.route('/master/posisi/getPosisiById/<posisi_id>', methods=['GET'])
@verifyLogin

def getPosisiById(posisi_id):
    response = {
        "error" : True,
        "message" : "",
        "data" : {}
    }
    
    try:
        posisi = Posisi.query.filter_by(status_enabled = True, posisi_id = posisi_id ).first()

        data = posisi.serialise()
        response["message"] = "Posisi found"
        response["error"] = False
        response["data"] = data
    except Exception as e:
        response["message"] = str(e)
    finally:
        db.session.close()

    
    return jsonify(response)



#################################################################################################
# GET KEPUTUSAN
#################################################################################################
@router.route('/master/keputusan/getAll', methods=['GET'])
@verifyLogin

def getAllKeputusan():
    response = {
        "error" : True,
        "message" : "",
        "data" : {}
    }
    
    try:
        keputusanEnabled = Keputusan.query.filter_by(status_enabled = True).order_by(Keputusan.keputusan_id).all()

        data = ([e.serialise() for e in keputusanEnabled])
        keputusanEnabledCount  = len(data)
        response["message"] = "Keputusan(s) found : " + str(keputusanEnabledCount)
        response["error"] = False
        response["data"] = data
    except Exception as e:
        response["message"] = str(e)
    finally:
        db.session.close()

    
    return jsonify(response)
