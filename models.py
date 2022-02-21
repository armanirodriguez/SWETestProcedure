import re
from app import app,db

class TestProcedure(db.Model):
    __tablename__ = 'testprocedure'
<<<<<<< HEAD
    pk_prodID = db.Column(db.Integer, primary_key=True)
    createdBy = db.Column(db.String, nullable=False)
    dateCreated = db.Column(db.String, nullable=False)
    prodName = db.Column(db.String(30), nullable=False)
    requirements = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(), nullable=False)
    priority = db.Column(db.String, nullable=False)
    estTimeToComplete = db.Column(db.String(), nullable=False)
=======
    pk_procedure = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
>>>>>>> bdce5f82078f97d1febc5c6d9bf6adb73b7f0b82
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
<<<<<<< HEAD
    pk_stepID = db.Column(db.Integer, primary_key=True)
    testStepName = db.Column(db.Text, nullable=False) # actual test step
    fk_prodID = db.Column(db.Integer, db.ForeignKey('testprocedure.pk_prodID'))
=======
    pk_step = db.Column(db.Integer, primary_key=True)
    test_step = db.Column(db.Text, nullable=False) # actual test step
    fk_TestStep_TestProcedure = db.Column(db.Integer, db.ForeignKey('testprocedure.id'))
>>>>>>> bdce5f82078f97d1febc5c6d9bf6adb73b7f0b82
    procedure = db.relationship('TestProcedure', backref="testprocedure")
    def __init__(self, test_step, procedure_fk_id):
        self.test_step = test_step
        self.procedure_id = procedure_fk_id



