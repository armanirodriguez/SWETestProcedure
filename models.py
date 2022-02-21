import re
from app import app,db

class TestProcedure(db.Model):
    __tablename__ = 'testprocedure'
    pk_prodID = db.Column(db.Integer, primary_key=True)
    createdBy = db.Column(db.String, nullable=False)
    dateCreated = db.Column(db.String, nullable=False)
    prodName = db.Column(db.String(30), nullable=False)
    requirements = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(), nullable=False)
    priority = db.Column(db.String, nullable=False)
    estTimeToComplete = db.Column(db.String(), nullable=False)
    version = db.Column(db.String(5), nullable=False)
    approval = db.Column(db.Boolean, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    steps = db.relationship('TestStep', backref='proc')
    def __init__(self, createdBy, dateCreated, prodName, requirements, status, priority, estTimeToComplete, 
                version, approval, notes):
        self.createdBy = createdBy
        self.dateCreated = dateCreated
        self.prodName = prodName
        self.requirements = requirements
        self.status = status
        self.priority = priority
        self.estTimeToComplete = estTimeToComplete
        self.version = version
        self.approval = approval
        self.notes = notes
        
class TestStep(db.Model):
    __tablename__ = 'teststep'
    pk_stepID = db.Column(db.Integer, primary_key=True)
    testStepName = db.Column(db.Text, nullable=False) # actual test step
    fk_prodID = db.Column(db.Integer, db.ForeignKey('testprocedure.pk_prodID'))
    procedure = db.relationship('TestProcedure', backref="testprocedure")
    def __init__(self, test_step, procedure_fk_id):
        self.test_step = test_step
        self.procedure_id = procedure_fk_id



