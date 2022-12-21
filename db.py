# DB functions for HBNetMon
#
# Copyright (C) 2020 Eric Craw, KF7EEL <kf7eel@qsl.net>
# https://github.com/kf7eel/HBNetMon

import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from datetime import datetime

engine = db.create_engine('sqlite:///local.db?check_same_thread=False')
connection = engine.connect()
db_session = scoped_session(sessionmaker(autocommit=False,
                                autoflush=False,
                                bind=engine))

Model = declarative_base(name='Model')
Model.query = db_session.query_property()
Model.metadata.create_all(bind=engine)

class local_db:

    def init_db(self):
        
        Model.metadata.create_all(bind=engine)

    class SvrConfig(Model):
        __tablename__ = 'server_configs'
        id = db.Column(db.Integer, primary_key=True)
        server_name = db.Column(db.String(10000), nullable=False)
        data = db.Column(db.String(10000), nullable=False)

    class txNow(Model):
        __tablename__ = 'tx_now'
        id = db.Column(db.Integer, primary_key=True)
        stream_id = db.Column(db.String(10000), primary_key=False)
        source = db.Column(db.String(10000), nullable=False)
        destination = db.Column(db.String(10000), nullable=False)
        start_time = db.Column(db.DateTime())

    class CallLog(Model):
        __tablename__ = 'call_log'
        id = db.Column(db.Integer, primary_key=True)
        stream_id = db.Column(db.String(10000), primary_key=False)
        source = db.Column(db.String(10000), nullable=False)
        call_type = db.Column(db.String(10000))
        destination = db.Column(db.String(10000), nullable=False)
        duration = db.Column(db.Float())
        slot = db.Column(db.Integer())

    def add_svr_config(self, name, data):
        c = self.SvrConfig(
            server_name=name,
            data = data
        )
        db_session.add(c)
        db_session.commit()

    def update_svr_config(self, id, data):
        record = self.self.SvrConfig.query.filter_by(id=id).first()
        record.data = data
        db_session.commit()

    def add_tx_now(self, source, dest, stream_id):
        print('add to db')
##        try:
##        current_stream = self.txNow.query.filter_by(stream_id = stream_id).first()
##        if current_stream == None:
##        except:
        tx = self.txNow(
            source = source,
            destination = dest,
            stream_id = stream_id,
            start_time = datetime.utcnow()
        )
        db_session.add(tx)
        db_session.commit()
##        elif current_stream != None:
##            print('------------------------- record exists -----------------')


    def add_call_log(self, source, dest, stream_id, call_type, duration, slot):
        print('add to db')
##        try:
##        current_stream = self.txNow.query.filter_by(stream_id = stream_id).first()
##        if current_stream == None:
##        except:
        cl = self.CallLog(
            source = source,
            destination = dest,
            stream_id = stream_id,
            duration =  duration,
            call_type = call_type,
            slot = slot
        )
        db_session.add(cl)
        db_session.commit()
        print('finish call log')
        
    def del_tx_now(self, source):
        tx = self.txNow.query.filter_by(source = source).first()
        print(tx)
        db_session.delete(tx)
        db_session.commit()

    def clear_tx_now(self):
        on_a = self.txNow.query.all()
        for i in on_a:
            db_session.delete(i)
        db_session.commit()

    def clear_db(self):
        on_a = self.txNow.query.all()
        for i in on_a:
            db_session.delete(i)
        db_session.commit()

