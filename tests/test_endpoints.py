def test_landing_page(client):
    response = client.get("/")
    assert response.status_code == 200


def test_login_page(client):
    response = client.get("/login")
    assert response.status_code == 200


def test_login_success(client, test_user):
    response = client.post(
        "/login",
        data={"email": "test@example.com", "password": "testpassword123"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies


def test_login_failure(client, test_user):
    response = client.post(
        "/login",
        data={"email": "test@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_protected_requires_auth(client):
    response = client.get("/protected", follow_redirects=False)
    assert response.status_code == 307
    assert "/login" in response.headers.get("location", "")


def test_protected_with_auth(client, test_user):
    # Login first to get cookies
    client.post(
        "/login",
        data={"email": "test@example.com", "password": "testpassword123"},
        follow_redirects=False,
    )
    # TestClient persists cookies, so /protected should work now
    response = client.get("/protected")
    assert response.status_code == 200
    assert "test@example.com" in response.json()["message"]


def test_logout_clears_cookies(client, test_user):
    # Login first
    client.post(
        "/login",
        data={"email": "test@example.com", "password": "testpassword123"},
        follow_redirects=False,
    )
    response = client.get("/logout")
    assert response.status_code == 200
    # After logout, protected route should redirect to login
    response = client.get("/protected", follow_redirects=False)
    assert response.status_code == 307
