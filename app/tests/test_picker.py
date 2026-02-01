def _login(client, email):
    client.post("/api/v1/auth/signup", json={"email": email, "password": "supersecret1"})
    r = client.post("/api/v1/auth/login", json={"email": email, "password": "supersecret1"})
    return r.json()["access_token"]

def test_picker_pick_history(client):
    token = _login(client, "picker@test.com")
    r = client.post("/api/v1/rooms", json={"name": "Picker Room"}, headers={"Authorization": f"Bearer {token}"})
    room_id = r.json()["id"]

    r = client.post(f"/api/v1/rooms/{room_id}/pickers", json={"name": "Picker"},
                    headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 201
    picker_id = r.json()["id"]

    client.post(f"/api/v1/pickers/{picker_id}/options", json={"label": "X"},
                headers={"Authorization": f"Bearer {token}"})
    client.post(f"/api/v1/pickers/{picker_id}/options", json={"label": "Y"},
                headers={"Authorization": f"Bearer {token}"})

    r = client.post(f"/api/v1/pickers/{picker_id}/pick", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["event_id"]

    r = client.get(f"/api/v1/pickers/{picker_id}/history", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert len(r.json()) >= 1
