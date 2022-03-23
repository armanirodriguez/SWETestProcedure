import os
import pytest

from SWETestProcedure.app import app, db


@pytest.fixture()
def app_fixture():

    app.config.update({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///test.db"})

    return app


@pytest.fixture()
def client(app_fixture):
    return app.test_client()


@pytest.fixture()
def runner(app_fixture):
    return app.test_cli_runner()


@pytest.fixture
def database(app_fixture):
    yield db
    os.remove("./app/test.db")


def test_assert_db(database):
    assert os.path.exists("./app/test.db")


def test_request_home(client):
    response = client.get("/home")
    assert (
        b"Welcome to the Great White Shark's Test Management Application!"
        in response.data
    )
