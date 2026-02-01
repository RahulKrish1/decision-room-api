def test_signup_and_login_and_me(client):
    # signup
    r = client.post("/api/v1/auth/signup", json={"email": "t1@test.com", "password": "supersecret1"})
    assert r.status_code in (201, 409)

    # login
    r = client.post("/api/v1/auth/login", json={"email": "t1@test.com", "password": "supersecret1"})
    assert r.status_code == 200
    token = r.json()["access_token"]
    assert token

    # me
    r = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["email"] == "t1@test.com"
