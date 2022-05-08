from app.models import User

def test_new_user():
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the id, username, password, and permission fields are defined correctly
    """
    user = User('1', 'test', 'password', 0,)
    assert user.id == '1'
    assert user.username == 'test'
    assert user.password == 'password'
    assert user.permissions == 0