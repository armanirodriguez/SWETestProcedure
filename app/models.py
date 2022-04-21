from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin


class TestProcedure(db.Model):
    __tablename__ = "TestProcedure"
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("Project.id"))
    name = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    approval = db.Column(db.Boolean, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    approvalNotes = db.Column(db.Text, nullable=True)
    steps = db.relationship("TestStep", backref="procedure", lazy=True)


class TestStep(db.Model):
    __tablename__ = "TestStep"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    pass_condition = db.Column(db.Text, nullable=False)
    is_setup_step = db.Column(db.Boolean, nullable=False, default=False)
    procedure_id = db.Column(db.Integer, db.ForeignKey("TestProcedure.id"))
    runs = db.relationship("TestRun", backref="step", lazy=True)


class Project(db.Model):
    __tablename__ = "Project"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    procedures = db.relationship("TestProcedure", backref="project", lazy=True)
    versions = db.relationship("Version", backref="project", lazy=True)


class Version(db.Model):
    __tablename__ = "Version"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("Project.id"))


class TestRun(db.Model):
    __tablename__ = "TestRun"
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    version_id = db.Column(db.Integer, db.ForeignKey("Version.id"))
    step_id = db.Column(db.Integer, db.ForeignKey("TestStep.id"))
    passing = db.Column(db.Boolean, nullable=False)
    notes = db.Column(db.Text, nullable=True)


class User(db.Model, UserMixin):
    # Bitmask for permissions
    PERM_EDIT = 1
    PERM_ADMIN = 1 << 1

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)
    permissions = db.Column(db.Integer, nullable=False, default=0)
    force_password_change = db.Column(db.Boolean, default=False)

    # Jinja does't have bitwise operations so we define a helper
    def is_admin(self):
        return self.permissions & self.PERM_ADMIN


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
