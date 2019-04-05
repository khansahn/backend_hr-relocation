
from flask import Flask, request, json, jsonify, make_response
import os, requests

from ..utils.models import *

from ..utils.authorisation import verifyLogin


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
        completed_at = None,
        submitted_by_id = body["user_login"]["npk"],
        record_id = requestDB.record_id)
    db.session.add(historyDB)
    db.session.commit()

    return requestDB


#####################################################################################################
# SUBMIT REQUEST (CREATE RECORD + SUBMIT RECORD)
#####################################################################################################
@router.route('/request/submit', methods = ['POST'])
@verifyLogin

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
@verifyLogin

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
@verifyLogin

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
    db.session.commit()

    historyDB = History(
        activity = body["action"],
        pegawai_id = body["data_pegawai_requested"]["npk"],
        posisi_id = body["data_pegawai_requested"]["posisi_id_awal"],
        request_id = requestDB.request_id,
        response = body["action"],
        started_at = requestDB.created_at,
        completed_at = None,
        submitted_by_id = body["user_login"]["npk"],
        record_id = requestDB.record_id)
    db.session.add(historyDB)
    db.session.commit()

    return requestDB


#####################################################################################################
# SUBMIT TASK 
#####################################################################################################
@router.route('/task/submit', methods = ['POST'])
@verifyLogin

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

        respTEST = {
            "submittedTaskDB" : submittedTaskDB.serialise(),
            "responNF" : submittedTask
        }            

        recordStageView = getRecordStageView(submittedTaskDB.record_id,tokenNFLogin)
        print("CEK 1",recordStageView['data'][-1]['type'])
        isRecordComplete = isRecordCompleted(recordStageView,body["data_pegawai_requested"], tokenNFLogin)

        recordStageViewAdmin = getRecordStageViewAdmin(submittedTaskDB.record_id)
        print("CEK 2",recordStageViewAdmin['data'][-1]['type'])
        isRecordCompleteAdmin = isRecordCompleted(recordStageViewAdmin,body["data_pegawai_requested"], tokenNFLogin)

        
        recordStageViewAdmin2 = getRecordStageViewAdmin(submittedTaskDB.record_id)
        print("CEK 3",recordStageViewAdmin2['data'][-1]['type'])
        isRecordCompleteAdmin2 = isRecordCompleted(recordStageViewAdmin2,body["data_pegawai_requested"], tokenNFLogin)

        additionalMessage = ""
        if (isRecordCompleteAdmin2["relocated"] == True) :
            relocatePegawaiWhenRecordIsCompleted(body["data_pegawai_requested"])
            additionalMessage = "Pegawai is relocated"

        response["message"] =  "Task submitted.   " + additionalMessage
        response["error"] = False
        response["data"] = respTEST
    except Exception as e:
        response["message"] = str(e)
    finally:
        db.session.close()

    return jsonify(response)





#####################################################################################################
# SUBMIT TASK REVISE
#####################################################################################################
@router.route('/task/submitrevise', methods = ['POST'])
@verifyLogin

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
@router.route('/history/getAll', methods=['GET'])
@verifyLogin
def getAllHistory():
    response = {
        "error" : True,
        "message" : "",
        "data" : {}
    }
            
    try:
        historyEnabled = db.session.query(History).filter_by(status_enabled = True).order_by(History.started_at).all()
        
        data = ([e.serialise() for e in historyEnabled])
        historyEnabledCount  = len(data)
        response["message"] = "History(s) found : " + str(historyEnabledCount)
        response["error"] = False
        response["data"] = data
    except Exception as e:
        response["message"] = str(e)
    finally:
        db.session.close()
        print("tes ok")
    
    return jsonify(response)


def getRecordStageViewAdmin(record_id):
    print("masuk record stage view admin")
    urlSubmitRecordNF = os.getenv("NEXTFLOW_SUBMITRECORD_URL")
    userTokenNF = os.getenv("NF_user_token")
    # userTokenNF = tokenNFLogin

    recordStageView = requests.get(urlSubmitRecordNF + record_id +'/stageview', headers = {"Authorization": "Bearer %s" %userTokenNF})
    print("mau keluar record stage view admin")
    return json.loads(recordStageView.text)


def getRecordStageView(record_id, tokenNFLogin):
    urlSubmitRecordNF = os.getenv("NEXTFLOW_SUBMITRECORD_URL")
    # userTokenNF = os.getenv("NF_user_token")
    userTokenNF = tokenNFLogin

    recordStageView = requests.get(urlSubmitRecordNF + record_id +'/stageview', headers = {"Authorization": "Bearer %s" %userTokenNF})

    return json.loads(recordStageView.text)

def isRecordCompleted(recordStageView, pegawaiRequested, tokenNFLogin):
    # print(recordStageView, pegawaiRequested)
    print(recordStageView['data'][-1]['type'])
    print(pegawaiRequested['npk'])

    print("func isrecordcomplete called")
    response = {
        "message" : "",
        "relocated" : False
    }

    #double check
    # doubleCheckRecordStageView = getRecordStageView(recordStageView['data'][-1]['record_id'], tokenNFLogin)
    # print("HASIL DOUBLE CHECK", doubleCheckRecordStageView['data'][-1]['type'] )
    # tripleCheckRecordStageView = getRecordStageView(recordStageView['data'][-1]['record_id'], tokenNFLogin)

    # print("HASIL TRIPLE CHECK", tripleCheckRecordStageView['data'][-1]['type'] )

    if (recordStageView['data'][-1]['type'] == "record:state:completed"):
        print("MASUK")
        # relocatePegawaiWhenRecordIsCompleted(pegawaiRequested)
        response["message"] = "record completed, pegawai relocated"
        response["relocated"] = True
        print("relocated")
    else :
        response["message"] = "process is still on going"

    return jsonify(response)


def relocatePegawaiWhenRecordIsCompleted(pegawaiRequested):
    print(pegawaiRequested['npk'])
    print("func relocatepegawaiwhenrecordiscompleted called")

    try:
        Pegawai.query.filter_by(npk = pegawaiRequested['npk']).update(dict(posisi_id=pegawaiRequested['posisi_id_tujuan']))
        message = "pegawai realocated"

        db.session.commit()
    
    except Exception as e:
        return str(e)
    finally:
        db.session.close()

    return message