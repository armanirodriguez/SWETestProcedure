from app import app,db








class TestProcedure(db.Model):
    __tablename__ = 'testprocedure'
    pk_procedure = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    version = db.Column(db.String(5), nullable=False)
    approval = db.Column(db.Boolean, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    steps = db.relationship('TestStep', backref='proc')
    def __init__(self, name, version, approval, notes):
        self.name = name
        self.version = version
        self.approval = approval
        self.notes = notes
        
class TestStep(db.Model):
    __tablename__ = 'teststep'
    pk_step = db.Column(db.Integer, primary_key=True)
    test_step = db.Column(db.Text, nullable=False) # actual test step
    fk_TestStep_TestProcedure = db.Column(db.Integer, db.ForeignKey('testprocedure.id'))
    procedure = db.relationship('TestProcedure', backref="testprocedure")
    def __init__(self, test_step, procedure_id):
        self.test_step = test_step
        self.procedure_id = procedure_id
