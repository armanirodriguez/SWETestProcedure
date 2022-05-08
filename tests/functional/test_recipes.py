def test_home_page():
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    app = app

    with app:
        response = app.get('/')
        assert response.status_code == 200