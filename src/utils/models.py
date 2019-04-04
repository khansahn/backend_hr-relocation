import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Pegawai(db.Model):
    __tablename__ = 'pegawai'

    npk = db.Column(db.Integer, primary_key = True)
    nama = db.Column(db.String())
    email = db.Column(db.String())
    password = db.Column(db.String())
    role_id = db.Column(db.Integer(), db.ForeignKey('role.role_id'))
    posisi_id = db.Column(db.Integer(), db.ForeignKey('posisi.posisi_id'))
    created_at = db.Column(db.DateTime, default =  datetime.datetime.now())
    updated_at = db.Column(db.DateTime)
    status_enabled = db.Column(db.Boolean(), default = True)  

    token_nf = db.Column(db.String())

    # role_name = db.relationship('Role',cascade="all,delete", backref='Quiz', lazy=True)


    def __init__(self,nama,email,password,role_id,posisi_id,token_nf):
        self.nama = nama
        self.email = email
        self.password = password
        self.role_id = role_id
        self.posisi_id = posisi_id
        self.token_nf = token_nf

    # buat ngereturn npk nya
    def __repr__(self):
        return '<pegawai npk {}>'.format(self.npk)

    def serialise(self):
        role = Role.query.filter_by(role_id = self.role_id).first()
        posisi = Posisi.query.filter_by(posisi_id = self.posisi_id).first()
        return {
            'npk' : self.npk,
            'nama' : self.nama,
            'email' : self.email,
            'password' : self.password,
            'role_id' : self.role_id,
            'posisi_id' : self.posisi_id,
            'role_name' : role.role_name,
            'posisi_name' : posisi.posisi_name,
            'status_enabled' : self.status_enabled,
            'token_nf' : self.token_nf
        }

    def returnToUser(self):
        role = Role.query.filter_by(role_id = self.role_id).first()
        posisi = Posisi.query.filter_by(posisi_id = self.posisi_id).first()

        return {
            'npk' : self.npk,
            'nama' : self.nama,
            'email' : self.email,
            # 'password' : self.password,
            'role_id' : self.role_id,
            'posisi_id' : self.posisi_id,
            'role_name' : role.role_name,
            'posisi_name' : posisi.posisi_name,
            'status_enabled' : self.status_enabled,
            'token_nf' : self.token_nf
        }

    def getDetailedPosisiOnPegawaiAtNPK(self):
        role = Role.query.filter_by(role_id = self.role_id).first()
        posisi = Posisi.query.filter_by(posisi_id = self.posisi_id).first()
        
        return {
            'npk' : self.npk,
            'nama' : self.nama,
            'email' : self.email,
            # 'password' : self.password,
            'role_id' : self.role_id,
            'posisi_id' : self.posisi_id,
            'role_name' : role.role_name,
            'posisi_name' : posisi.posisi_name,
            'status_enabled' : self.status_enabled,
            'posisi' : {
                'posisi_id' : self.posisi_id,
                'posisi_name' : posisi.posisi_name,
                'posisi_type' : posisi.posisi_type,
                'area' : posisi.area,
                'company' : posisi.company
            }
        }

    def getEmail(self) :
        return self.email

    def getName(self) :
        return self.nama
    

###############################################

class Posisi(db.Model):
    __tablename__ = 'posisi'

    posisi_id = db.Column(db.Integer, primary_key = True)
    posisi_name = db.Column(db.String())
    posisi_type = db.Column(db.String())
    company = db.Column(db.String())
    area = db.Column(db.String())
    # creator_id = db.Column(db.Integer(), db.ForeignKey('registereduser.user_id'))
    created_at = db.Column(db.DateTime, default =  datetime.datetime.now())
    updated_at = db.Column(db.DateTime)
    status_enabled = db.Column(db.Boolean(), default = True)
    # question_list = db.Column(db.Integer())
    # question = db.relationship('Question',cascade="all,delete", backref='Quiz', lazy=True)


    def __init__(self,posisi_name,posisi_type,area,company):
        self.posisi_name = posisi_name
        self.posisi_type = posisi_type
        self.area = area
        self.company = company

    def __repr__(self):
        return '<posisi id {}>'.format(self.posisi_id)

    def serialise(self):
        return {
            'posisi_id' : self.posisi_id,
            'posisi_name' : self.posisi_name,
            'posisi_type' : self.posisi_type,
            'company' : self.company,
            'area' : self.area,
            'status_enabled' : self.status_enabled,
            # 'question_list' : [{'question_id': e.question_id, 'question' : e.question, 'status_enabled': e.status_enabled} for e in self.question]
        }

    # def getAllEnabled(self):
    #     posisiEnabled = Posisi.query.filter_by(status_enabled = True).order_by(Posisi.posisi_id).all()

        




###############################################

class Role(db.Model):
    __tablename__ = 'role'

    role_id = db.Column(db.Integer, primary_key = True)
    # quiz_id = db.Column(db.Integer(), db.ForeignKey('quiz.quiz_id'), nullable= False)
    role_name = db.Column(db.String())
    created_at = db.Column(db.DateTime, default =  datetime.datetime.now())
    updated_at = db.Column(db.DateTime)
    status_enabled = db.Column(db.Boolean(), default = True)
    # options = db.Column(db.String())
    # options = db.relationship('Options',cascade="all,delete", backref='Question', lazy=True)
    posisi_id = db.Column(db.Integer(), db.ForeignKey('posisi.posisi_id'))

    def __init__(self,role_name, posisi_id):
        self.role_name = role_name
        self.posisi_id = posisi_id

    def __repr__(self):
        return '<role id {}>'.format(self.role_id)

    def serialise(self):
        posisi = Posisi.query.filter_by(posisi_id = self.posisi_id).first()
        return {
            'role_id' : self.role_id,
            'role_name' : self.role_name,
            'posisi_id' : self.posisi_id,
            'posisi_name' : posisi.posisi_name,
            'status_enabled' : self.status_enabled
        }
        
    
###############################################
class Request(db.Model):
    __tablename__ = 'request'

    request_id = db.Column(db.Integer, primary_key = True)
    process_id = db.Column(db.String())
    record_id = db.Column(db.String())
    comment = db.Column(db.String())
    requester_id = db.Column(db.Integer(), db.ForeignKey('pegawai.npk'))
    requester_email = db.Column(db.String())
    hrdeptasal_email = db.Column(db.String())
    hrperusahaan_email = db.Column(db.String())
    mandepttujuan_email = db.Column(db.String())
    seniormanperusahaan_email = db.Column(db.String())
    hrdepttujuan_email = db.Column(db.String())

    behalf_name = db.Column(db.String())
    behalf_posisi = db.Column(db.String())
    action = db.Column(db.String())
    keputusan_id = db.Column(db.Integer(), db.ForeignKey('keputusan.keputusan_id'))
    requested_id = db.Column(db.Integer(), db.ForeignKey('pegawai.npk'))
    requested_email = db.Column(db.Integer(), db.ForeignKey('pegawai.email'))

    # created at nya bisa diedit ga
    created_at = db.Column(db.DateTime, default =  datetime.datetime.now())
    updated_at = db.Column(db.DateTime)
    effective_date = db.Column(db.DateTime)
    status_enabled = db.Column(db.Boolean(), default = True)

    posisi_id_awal = db.Column(db.Integer(), db.ForeignKey('posisi.posisi_id'))
    posisi_id_tujuan = db.Column(db.Integer(), db.ForeignKey('posisi.posisi_id'))
    role_id_awal = db.Column(db.Integer(), db.ForeignKey('role.role_id'))
    role_id_tujuan = db.Column(db.Integer(), db.ForeignKey('role.role_id'))



    def __init__(self,process_id,record_id,comment,requester_id,requester_email,hrdeptasal_email,hrperusahaan_email,mandepttujuan_email,seniormanperusahaan_email,hrdepttujuan_email,behalf_name,behalf_posisi,action,keputusan_id,effective_date,requested_id,requested_email, posisi_id_awal, posisi_id_tujuan, role_id_awal, role_id_tujuan):
        self.process_id = process_id
        self.record_id = record_id
        self.comment = comment
        self.requester_id = requester_id
        self.requester_email = requester_email
        self.hrdeptasal_email = hrdeptasal_email
        self.hrperusahaan_email = hrperusahaan_email
        self.mandepttujuan_email = mandepttujuan_email
        self.seniormanperusahaan_email = seniormanperusahaan_email
        self.hrdepttujuan_email = hrdepttujuan_email
        self.behalf_name = behalf_name
        self.behalf_posisi = behalf_posisi
        self.action = action
        self.keputusan_id = keputusan_id
        self.effective_date = effective_date
        self.requested_id = requested_id
        self.requested_email = requested_email
        self.posisi_id_awal = posisi_id_awal
        self.posisi_id_tujuan = posisi_id_tujuan
        self.role_id_awal = role_id_awal
        self.role_id_tujuan = role_id_tujuan
        
    def __repr__(self):
        return '<request id {}>'.format(self.request_id)

    def serialise(self):        
        requester = Pegawai.query.filter_by(npk = self.requester_id).first()
        requesterPosisi = Posisi.query.filter_by(posisi_id = requester.posisi_id).first()
        hrdeptasal = Pegawai.query.filter_by(email = self.hrdeptasal_email).first()
        hrperusahaan = Pegawai.query.filter_by(email = self.hrperusahaan_email).first()
        mandepttujuan = Pegawai.query.filter_by(email = self.mandepttujuan_email).first()
        seniormanperusahaan = Pegawai.query.filter_by(email = self.seniormanperusahaan_email).first()
        hrdepttujuan = Pegawai.query.filter_by(email = self.hrdepttujuan_email).first()
        requested = Pegawai.query.filter_by(npk = self.requested_id).first()
        requestedPosisi = Posisi.query.filter_by(posisi_id = requested.posisi_id).first()
        posisiAwal = Posisi.query.filter_by(posisi_id = self.posisi_id_awal).first()
        posisiTujuan = Posisi.query.filter_by(posisi_id = self.posisi_id_tujuan).first()
        roleAwal = Role.query.filter_by(role_id = self.role_id_awal).first()
        roleTujuan = Role.query.filter_by(role_id = self.role_id_tujuan).first()

        keputusanExist = db.session.query(Keputusan).filter_by(keputusan_id = self.keputusan_id).scalar() is not None
        if (keputusanExist == True) :
            keputusan = Keputusan.query.filter_by(keputusan_id = self.keputusan_id).first()
            keputusan_name = keputusan.keputusan_name
            keputusan_id = keputusan.keputusan_id
        else:
            keputusan_name = ""
            keputusan_id = 0

        
        return {
            'request_id' : self.request_id,
            'process_id' : self.process_id,
            'record_id' : self.record_id,
            'comment' : self.comment,
            'requester_id' : self.requester_id,
            'requester_email' : requester.email,
            'requester_name' : requester.nama,
            'requester_posisi_name' : requesterPosisi.posisi_name,
            'hrdeptasal_email' : hrdeptasal.email,
            'hrdeptasal_name' : hrdeptasal.nama,
            'hrperusahaan_email' : hrperusahaan.email,
            'hrperusahaan_name' : hrperusahaan.nama,
            'mandepttujuan_email' : mandepttujuan.email,
            'mandepttujuan_name' : mandepttujuan.nama,
            'seniormanperusahaan_email' : seniormanperusahaan.email,
            'seniormanperusahaan_name' : seniormanperusahaan.nama,
            'hrdepttujuan_email' : hrdepttujuan.email,
            'hrdepttujuan_name' : hrdepttujuan.nama,
            'behalf_name' : self.behalf_name,
            'behalf_posisi' : self.behalf_posisi,
            'status_enabled' : self.status_enabled,
            'created_at' : self.created_at,
            'action' : self.action,
            'keputusan_id' : keputusan_id,
            'keputusan_name' : keputusan_name,
            'effective_data' : self.effective_date,
            'requested_id' : requested.npk,
            'requested_email' : requested.email,
            'requested_name' : requested.nama,
            'requested_posisi_name' : requestedPosisi.posisi_name,
            'posisi_id_awal' : posisiAwal.posisi_id,
            'posisi_id_awal_name' : posisiAwal.posisi_name,
            'posisi_id_tujuan' : posisiTujuan.posisi_id,
            'posisi_id_tujuan_name' : posisiTujuan.posisi_name,
            'role_id_awal' : roleAwal.role_id,
            'role_id_awal_name' : roleAwal.role_name,
            'role_id_tujuan' : roleTujuan.role_id,
            'role_id_tujuan_name' : roleTujuan.role_name,
            'company_awal' : posisiAwal.company,
            'company_tujuan' : posisiTujuan.company,
            'area_awal' : posisiAwal.area,
            'area_tujuan' : posisiTujuan.area,
            'posisi_tujuan_type' : posisiTujuan.posisi_type,
            'posisi_awal_type' : posisiAwal.posisi_type   

        }


###############################################

class History(db.Model):
    __tablename__ = 'history'

    history_id = db.Column(db.Integer, primary_key = True)
    history_name = db.Column(db.String())
    activity = db.Column(db.String())
    pegawai_id = db.Column(db.Integer(), db.ForeignKey('pegawai.npk'), nullable = False)
    posisi_id = db.Column(db.Integer(), db.ForeignKey('posisi.posisi_id'), nullable = False)
    request_id = db.Column(db.Integer(), db.ForeignKey('request.request_id'), nullable = False)
    response = db.Column(db.String())
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    status_enabled = db.Column(db.Boolean(), default = True)

    def __init__(self,activity,pegawai_id,posisi_id,request_id,response,started_at,completed_at):
        self.activity = activity
        self.pegawai_id = pegawai_id
        self.posisi_id = posisi_id
        self.request_id = request_id
        self.response = response
        self.started_at = started_at
        self.completed_at = completed_at

    def __repr__(self):
        return '<history id {}>'.format(self.history_id)

    def serialise(self):        
        pegawai = Pegawai.query.filter_by(npk = self.pegawai_id).first()
        posisi = Posisi.query.filter_by(posisi_id = self.posisi_id).first()
        return {
            'history_id' : self.history_id,
            'history_name' : self.history_name,
            'activity' : self.activity,
            'pegawai_id' : self.pegawai_id,
            'posisi_id' : self.posisi_id,
            'pegawai_name' : pegawai.nama,
            'posisi_name' : posisi.posisi_name,
            'request_id' : self.request_id,
            'response' : self.response,
            'started_at' : self.started_at,
            'completed_at' : self.completed_at,
            'status_enabled' : self.status_enabled
        }
        

###############################################

class Keputusan(db.Model):
    __tablename__ = 'keputusan'

    keputusan_id = db.Column(db.Integer, primary_key = True)
    keputusan_name = db.Column(db.String())
    created_at = db.Column(db.DateTime, default =  datetime.datetime.now())
    updated_at = db.Column(db.DateTime)
    status_enabled = db.Column(db.Boolean(), default = True)

    def __init__(self,keputusan_name):
        self.keputusan_name = keputusan_name

    def __repr__(self):
        return '<keputusan id {}>'.format(self.keputusan_id)

    def serialise(self):
        return {
            'keputusan_id' : self.keputusan_id,
            'keputusan_name' : self.keputusan_name,
            'status_enabled' : self.status_enabled
        }
        
    

    # def serialise(self):
    #     userscore = [{'username': e.username, 'score': e.score} for e in self.userscore]
    #     userscore.sort(key = lambda x: x['score'], reverse=True)
    #     print(userscore[0]['score'])
    #     return {
    #         'leaderboard_id' : self.leaderboard_id,
    #         'quiz_id' : self.quiz_id,
    #         'game_id' : self.game_id,
    #         'status_enabled': self.status_enabled,
    #         'userscore' : userscore
    #     }

        
        