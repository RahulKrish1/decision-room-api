def _login(client, email):
    client.post("/api/v1/auth/signup", json={"email": email, "password": "supersecret1"})
    r = client.post("/api/v1/auth/login", json={"email": email, "password": "supersecret1"})
    return r.json()["access_token"]

def test_poll_vote_results(client):
    token = _login(client, "poll@test.com")
    r = client.post("/api/v1/rooms", json={"name": "Poll Room"}, headers={"Authorization": f"Bearer {token}"})
    room_id = r.json()["id"]

    r = client.post(
        f"/api/v1/rooms/{room_id}/polls",
        json={"question": "Where?", "options": ["A", "B", "C"]},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 201
    poll_id = r.json()["id"]
    option_id = r.json()["options"][0]["id"]

    r = client.post(f"/api/v1/polls/{poll_id}/vote", json={"option_id": option_id},
                    headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 204

    r = client.get(f"/api/v1/polls/{poll_id}/results", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert any(row["option_id"] == option_id and row["votes"] == 1 for row in r.json())
