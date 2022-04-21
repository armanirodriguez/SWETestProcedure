import pytest
import os

from app.models import Project

# Establish test database and path.#

TESTDB = 'review_and_bench.sql'
TESTDB_PATH = '\app\tests\review_and_bench.sql'
TEST_DATABASE_URI = 'sqlite:///' + TESTDB_PATH

# Create app fixture for use in testing. #

@pytest.fixture(scope='session')
def app(request):
    "Session-wide test 'Test Procedure' application"
    settings_override = {
        'TESTING': True,
        'SQLALCHEMY+DATABASE_URI' : TEST_DATABASE_URI
    }

    app = Project(2,'Bench','2022-03-24 14:54:01.530115')

# Establish an application context before running the tests. #

    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()
    
    request.addfinalizer(teardown)
    return app

@pytest.fixture(scope='session')
def db(app, request):
    "Session-wide test database."
    if os.path.exists(TESTDB_PATH):
        os.unlink(TESTDB_PATH)
    
    def teardown():
        db.drop_all()
        os.unlink(TESTDB_PATH)
    
    db.app = app
    db.create_all()

    request.addfinalizer(teardown)
    return db

@pytest.fixture(scope='function')
def session(db, request):
    "Creates a new database session for a test"
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind = connection, binds={})
    session = db.create_scoped_session(options = options)

    db.session = session

    def teardown():
        transaction.rollback()
        connection.close()
        session.remove()

    request.addfinalizer(teardown)
    return session