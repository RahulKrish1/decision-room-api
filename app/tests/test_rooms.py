def _login(client, email="room@test.com"):
    client.post("/api/v1/auth/signup", json={"email": email, "password": "supersecret1"})
    r = client.post("/api/v1/auth/login", json={"email": email, "password": "supersecret1"})
    return r.json()["access_token"]

def test_create_room_and_list(client):
    token = _login(client)

    r = client.post("/api/v1/rooms", json={"name": "Test Room"}, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 201
    room = r.json()
    assert room["invite_code"]

    r = client.get("/api/v1/rooms", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert any(x["id"] == room["id"] for x in r.json())

def test_join_room_second_user(client):
    token1 = _login(client, "owner@test.com")
    r = client.post("/api/v1/rooms", json={"name": "Joinable"}, headers={"Authorization": f"Bearer {token1}"})
    invite = r.json()["invite_code"]
    room_id = r.json()["id"]

    token2 = _login(client, "member@test.com")
    r = client.post("/api/v1/rooms/join", json={"invite_code": invite}, headers={"Authorization": f"Bearer {token2}"})
    assert r.status_code == 200
    assert r.json()["id"] == room_id
