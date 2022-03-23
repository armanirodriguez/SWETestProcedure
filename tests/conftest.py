import pytest
from app import app


from flask import Flask

def test_base_route() :
    app = Flask(__name__)
    

