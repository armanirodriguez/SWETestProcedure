from datetime import datetime
from app import app,db

class TestProcedure(db.Model):
    __tablename__ = 'TestProcedure'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    approval = db.Column(db.Boolean, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    steps = db.relationship('TestStep', backref='procedure', lazy=True)


class TestStep(db.Model):
    __tablename__ = 'TestStep'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    status = db.Column(db.Integer, nullable=False, default=0)
    procedure_id = db.Column(db.Integer, db.ForeignKey('TestProcedure.id'))
