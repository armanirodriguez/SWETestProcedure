from flask_sqlalchemy import SQLAlchemy
from main import app

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

class TestProcedure(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    steps = db.relationship('TestStep', backref='procedure', lazy=True)

class TestStep(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_step = db.Column(db.Text, nullable=False) # actual test step
    procedure_id = db.Column(db.Integer, db.ForeignKey('TestProcedure.id'))