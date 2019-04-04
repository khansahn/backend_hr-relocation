
from flask import Flask, request, json, jsonify, make_response
import os, requests

from ..utils.models import *

from . import router

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import exists
from sqlalchemy import func

# NANTI TOKENNYA GANTI AMBIL DARI TABEL PEGAWAI((UDAHHH))

def queryNyariPegawaiDiPosisiRoleTerkait(posisi_id,role_name):
    #nyari role hrd
    idRoleHRD = db.session.query(Role).filter_by(posisi_id = posisi_id, role_name = role_name).first()
    #nyari hrd dept asal
    pegawaiTerkait = db.session.query(Pegawai).filter_by(posisi_id = posisi_id, role_id = idRoleHRD.role_id).first()

    return pegawaiTerkait


def createRecordNF(tokenNFRequester):
    # create record ke nextflow dl
    dataCreateRecordNF= {
	                    "data": {
                            "definition": {
                                "id": os.getenv("NF_definitions_bpmn")
			                }
		                }
                    }
    urlCreateRecordNF = os.getenv("NEXTFLOW_CREATERECORD_URL")
    # userTokenNF = os.getenv("NF_user_token") 
    userTokenNF = tokenNFRequester

    recordNF = requests.post(urlCreateRecordNF, data = json.dumps(dataCreateRecordNF), headers = {"Content-Type": "application/json", "Authorization": "Bearer %s" %userTokenNF})

    return json.loads(recordNF.text)

def submitRecordNF(recordIdNF, body, tokenNFRequester):   
    pegawaiRequester = db.session.query(Pegawai).filter_by(npk = body["data_pegawai_requester"]["npk"]).first()
    
    hrDeptAsal = queryNyariPegawaiDiPosisiRoleTerkait(body["data_pegawai_requested"]["posisi_id_awal"],"HRD")
    manDeptTujuan = queryNyariPegawaiDiPosisiRoleTerkait(body["data_pegawai_requested"]["posisi_id_tujuan"],"Manajer")
    hrDeptTujuan = queryNyariPegawaiDiPosisiRoleTerkait(body["data_pegawai_requested"]["posisi_id_tujuan"],"HRD")    

    dataSubmitRecordNF= {
        "data": {
            "form_data" : {
                "approver": " ",
                "requester" : pegawaiRequester.nama,
                "hrdeptasal" : hrDeptAsal.nama,
                "hrperusahaan" : "Hasna Nabila Khansa",
                "mandepttujuan" : manDeptTujuan.nama,
                "seniormanperusahaan" : "Akmaluddin F",
                "hrdepttujuan" : hrDeptTujuan.nama,			
                "email_requester": pegawaiRequester.email,
                "email_hrdeptasal": hrDeptAsal.email,
                "email_hrperusahaan": "snabilakhansa@gmail.com",
                "email_mandepttujuan": manDeptTujuan.email,
                "email_seniormanperusahaan": "akmaluddinfadhilah@gmail.com",
                "email_hrdepttujuan": hrDeptTujuan.email,
                "action" : "submit"
            },
            "comment": body["comment"]
            }
        }
    urlSubmitRecordNF = os.getenv("NEXTFLOW_SUBMITRECORD_URL")
    # userTokenNF = os.getenv("NF_user_token")
    userTokenNF = tokenNFRequester

    submitNF = requests.post(urlSubmitRecordNF+recordIdNF+'/submit', data = json.dumps(dataSubmitRecordNF), headers = {"Content-Type": "application/json", "Authorization": "Bearer %s" %userTokenNF})

    return json.loads(submitNF.text)

def submitRecordDB(pegawaiRequester,body):
    hrDeptAsal = queryNyariPegawaiDiPosisiRoleTerkait(body["data_pegawai_requested"]["posisi_id_awal"],"HRD")
    manDeptTujuan = queryNyariPegawaiDiPosisiRoleTerkait(body["data_pegawai_requested"]["posisi_id_tujuan"],"Manajer")
    hrDeptTujuan = queryNyariPegawaiDiPosisiRoleTerkait(body["data_pegawai_requested"]["posisi_id_tujuan"],"HRD")
    pegawaiRequested = db.session.query(Pegawai).filter_by(npk = body["data_pegawai_requested"]["npk"]).first()

    requestDB = Request(
        process_id = body["process_id"],
        record_id = body["record_id"],
        comment = body["comment"],
        requester_id = pegawaiRequester.npk,
        requester_email = pegawaiRequester.npk,
        hrdeptasal_email = hrDeptAsal.email,
        hrperusahaan_email = "snabilakhansa@gmail.com",
        mandepttujuan_email = manDeptTujuan.email,
        seniormanperusahaan_email = "akmaluddinfadhilah@gmail.com",
        hrdepttujuan_email = hrDeptTujuan.email,
        behalf_name = body["data_pegawai_requester"]["behalf_name"],
        behalf_posisi = body["data_pegawai_requester"]["behalf_posisi"],
        action = body["action"],
        keputusan_id = None,
        effective_date = body["effective_date"],
        requested_id = pegawaiRequested.npk,
        requested_email = pegawaiRequested.email,
        posisi_id_awal = body["data_pegawai_requested"]["posisi_id_awal"],
        posisi_id_tujuan = body["data_pegawai_requested"]["posisi_id_tujuan"],
        role_id_awal = body["data_pegawai_requested"]["role_id_awal"],
        role_id_tujuan = body["data_pegawai_requested"]["role_id_tujuan"])
    db.session.add(requestDB)
    db.session.commit()

    historyDB = History(
        activity = body["action"],
        pegawai_id = body["data_pegawai_requested"]["npk"],
        posisi_id = body["data_pegawai_requested"]["posisi_id_awal"],
        request_id = requestDB.request_id,
        response = body["action"],
        started_at = requestDB.created_at,
        completed_at = None)
    db.session.add(historyDB)
    db.session.commit()

    return requestDB


#####################################################################################################
# SUBMIT REQUEST (CREATE RECORD + SUBMIT RECORD)
#####################################################################################################
@router.route('/request/submit', methods = ['POST'])
def submitRequest():
    body = request.json

    response = {
        "error" : True,
        "message" : "",
        "data" : {}
    }
    errorCode = 404

    try:  
        pegawaiRequester = db.session.query(Pegawai).filter_by(npk = body["data_pegawai_requester"]["npk"]).first()
        tokenNFRequester = pegawaiRequester.token_nf

        recordNF = createRecordNF(tokenNFRequester) 
        recordIdNF = recordNF['data']['id']

        body["record_id"] = recordIdNF

        submittedRecord = submitRecordNF(recordIdNF,body,tokenNFRequester)
        processIdNF = submittedRecord['data']['process_id']

        body["process_id"] = processIdNF

        submittedRecordDB = submitRecordDB(pegawaiRequester,body)

        response["message"] =  "Request created. Request-id = {}".format(submittedRecordDB.request_id)
        response["error"] = False
        response["data"] = submittedRecordDB.serialise()
    except Exception as e:
        response["message"] = str(e)
    finally:
        db.session.close()

    return jsonify(response)


###########################################################################


def getTaskFromNF(tokenNFPegawai):
    # get task dari nextflow dl
    urlGetTaskFromNF = os.getenv("NEXTFLOW_GETLISTTASK_URL")
    urlGetTaskFilterFromNF = os.getenv("NEXTFLOW_GETLISTTASK_FILTER_URL")
    # userTokenNF = os.getenv("NF_user_token")
    userTokenNF = tokenNFPegawai

    listTaskNF = requests.get(urlGetTaskFromNF+urlGetTaskFilterFromNF, headers = {"Content-Type": "application/json", "Authorization": "Bearer %s" %userTokenNF})

    return json.loads(listTaskNF.text)


#################################################################################################
# GET REQUEST PER ID LOGIN (GET TASK) NANTI KEMBANGIN JADI PER USER TOKENNF STLH DAPET NPK
#################################################################################################
@router.route('/task/getAll/<npk>', methods=['GET'])
def getAllTasksById(npk):
    response = {
        "error" : True,
        "message" : "",
        "data" : {}
    }

    pegawai = db.session.query(Pegawai).filter_by(npk = npk).first()
    tokenNFPegawai = pegawai.token_nf
    
    try:
        listTask = getTaskFromNF(tokenNFPegawai)
        response["message"] = "Task(s) found"
        response["error"] = False
        response["data"] = listTask
    except Exception as e:
        response["message"] = str(e)
    finally:
        db.session.close()
    
    return jsonify(response)



#################################################################################################
# GET REQUEST PER REQUEST ID DARI LIST TASK (YANG UDAH PER TOKEN DARI NF-NYA) ini mah manggil dari local db aja
#################################################################################################
@router.route('/task/getTaskPerRecordId/<record_id>', methods=['GET'])
def getTaskPerRecordId(record_id):
    response = {
        "error" : True,
        "message" : "",
        "data" : {}
    }

    # pegawai = db.session.query(Pegawai).filter_by(npk = npk).first()
    # tokenNFPegawai = pegawai.token_nf

    request = db.session.query(Request).filter_by(record_id = record_id).first()
    
    try:        
        response["message"] = "Request found"
        response["error"] = False
        response["data"] = request.serialise()
    except Exception as e:
        response["message"] = str(e)
    finally:
        db.session.close()
    
    return jsonify(response)



######################################################################


def submitTaskNF(taskIdNF, body,tokenNFLogin, action):   
    pegawaiRequester = db.session.query(Pegawai).filter_by(npk = body["data_pegawai_requester"]["npk"]).first()
    
    hrDeptAsal = queryNyariPegawaiDiPosisiRoleTerkait(body["data_pegawai_requested"]["posisi_id_awal"],"HRD")
    manDeptTujuan = queryNyariPegawaiDiPosisiRoleTerkait(body["data_pegawai_requested"]["posisi_id_tujuan"],"Manajer")
    hrDeptTujuan = queryNyariPegawaiDiPosisiRoleTerkait(body["data_pegawai_requested"]["posisi_id_tujuan"],"HRD")   

    dataSubmitTaskNF= {
        "data": {
            "form_data" : {
                "action" : body["action"],
                "approver": " ",
                "requester" : pegawaiRequester.nama,
                "hrdeptasal" : hrDeptAsal.nama,
                "hrperusahaan" : "Hasna Nabila Khansa",
                "mandepttujuan" : manDeptTujuan.nama,
                "seniormanperusahaan" : "Akmaluddin F",
                "hrdepttujuan" : hrDeptTujuan.nama,			
                "email_requester": pegawaiRequester.email,
                "email_hrdeptasal": hrDeptAsal.email,
                "email_hrperusahaan": "snabilakhansa@gmail.com",
                "email_mandepttujuan": manDeptTujuan.email,
                "email_seniormanperusahaan": "akmaluddinfadhilah@gmail.com",
                "email_hrdepttujuan": hrDeptTujuan.email
            },
            "comment": body["comment"]
            }
        }
    urlSubmitTaskNF = os.getenv("NEXTFLOW_SUBMITTASK_URL")
    # userTokenNF = os.getenv("NF_user_token")
    userTokenNF = tokenNFLogin

    submitTaskNF = requests.post(urlSubmitTaskNF+taskIdNF+'/submit', data = json.dumps(dataSubmitTaskNF), headers = {"Content-Type": "application/json", "Authorization": "Bearer %s" %userTokenNF})

    return json.loads(submitTaskNF.text)

def submitTaskDB(body):
    hrDeptAsal = queryNyariPegawaiDiPosisiRoleTerkait(body["data_pegawai_requested"]["posisi_id_awal"],"HRD")
    manDeptTujuan = queryNyariPegawaiDiPosisiRoleTerkait(body["data_pegawai_requested"]["posisi_id_tujuan"],"Manajer")
    hrDeptTujuan = queryNyariPegawaiDiPosisiRoleTerkait(body["data_pegawai_requested"]["posisi_id_tujuan"],"HRD")
    pegawaiRequested = db.session.query(Pegawai).filter_by(npk = body["data_pegawai_requested"]["npk"]).first()
    pegawaiRequester = db.session.query(Pegawai).filter_by(npk = body["data_pegawai_requester"]["npk"]).first()

    requestDB = Request(
        process_id = body["process_id"],
        record_id = body["record_id"],
        comment = body["comment"],
        requester_id = pegawaiRequester.npk,
        requester_email = pegawaiRequester.npk,
        hrdeptasal_email = hrDeptAsal.email,
        hrperusahaan_email = "snabilakhansa@gmail.com",
        mandepttujuan_email = manDeptTujuan.email,
        seniormanperusahaan_email = "akmaluddinfadhilah@gmail.com",
        hrdepttujuan_email = hrDeptTujuan.email,
        behalf_name = body["data_pegawai_requester"]["behalf_name"],
        behalf_posisi = body["data_pegawai_requester"]["behalf_posisi"],
        action = body["action"],
        keputusan_id = body["keputusan_id"],
        effective_date = body["effective_date"],
        requested_id = pegawaiRequested.npk,
        requested_email = pegawaiRequested.email,
        posisi_id_awal = body["data_pegawai_requested"]["posisi_id_awal"],
        posisi_id_tujuan = body["data_pegawai_requested"]["posisi_id_tujuan"],
        role_id_awal = body["data_pegawai_requested"]["role_id_awal"],
        role_id_tujuan = body["data_pegawai_requested"]["role_id_tujuan"])
    db.session.add(requestDB)
    print("ADDED")
    db.session.commit()

    historyDB = History(
        activity = body["action"],
        pegawai_id = body["data_pegawai_requested"]["npk"],
        posisi_id = body["data_pegawai_requested"]["posisi_id_awal"],
        request_id = requestDB.request_id,
        response = body["action"],
        started_at = requestDB.created_at,
        completed_at = None)
    db.session.add(historyDB)
    print("ADDED History")
    db.session.commit()

    return requestDB


#####################################################################################################
# SUBMIT TASK 
#####################################################################################################
@router.route('/task/submit', methods = ['POST'])
def submitTask():
    body = request.json

    response = {
        "error" : True,
        "message" : "",
        "data" : {}
    }
    errorCode = 404
    
    try:
        pegawai = db.session.query(Pegawai).filter_by(npk = body["user_login"]["npk"]).first()
        tokenNFLogin = pegawai.token_nf

        submittedTask = submitTaskNF(body["task_id"],body,tokenNFLogin,body["action"])

        submittedTaskDB = submitTaskDB(body)                

        response["message"] =  "Task submitted."
        response["error"] = False
        response["data"] = submittedTaskDB.serialise()
    except Exception as e:
        response["message"] = str(e)
    finally:
        db.session.close()

    return jsonify(response)





#####################################################################################################
# SUBMIT TASK REVISE
#####################################################################################################
@router.route('/task/submitrevise', methods = ['POST'])
def submitTaskRevise():
    body = request.json

    response = {
        "error" : True,
        "message" : "",
        "data" : {}
    }
    errorCode = 404
    
    try:
        pegawai = db.session.query(Pegawai).filter_by(npk = body["user_login"]["npk"]).first()
        tokenNFLogin = pegawai.token_nf

        submittedTask = submitTaskNF(body["task_id"],body,tokenNFLogin,body["action"])

        submittedTaskDB = submitTaskDB(body)                

        response["message"] =  "Task submitted."
        response["error"] = False
        response["data"] = submittedTaskDB.serialise()
    except Exception as e:
        response["message"] = str(e)
    finally:
        db.session.close()

    return jsonify(response)



#################################################################################################
# GET ALL HISTORY
#################################################################################################
'''
@router.route('/history/getAll', methods=['GET'])
def getAllHistory():
    response = {
        "error" : True,
        "message" : "",
        "data" : {}
    }
    
    history = db.session.query(History).order_by(History.created_at).all()
        
    try:
        listTask = getTaskFromNF(tokenNFPegawai)
        response["message"] = "Task(s) found"
        response["error"] = False
        response["data"] = listTask
    except Exception as e:
        response["message"] = str(e)
    finally:
        # db.session.close()
        print("tes ok")
    
    return jsonify(response)
'''
