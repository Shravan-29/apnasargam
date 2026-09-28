from tests.conftest import register_and_login

PROJECT = {"name": "Test Track", "genre": "Jazz", "mood": "Calm", "bpm": 90, "musical_key": "C Major"}

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_register_never_returns_password(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "a@apnasargam.com", "password": "password123"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "a@apnasargam.com"
    assert "password" not in body
    assert "password_hash" not in body

def test_duplicate_registration_is_rejected(client):
    payload = {"email": "dup@apnasargam.com", "password": "password123"}
    assert client.post("/api/v1/auth/register", json=payload).status_code == 201
    assert client.post("/api/v1/auth/register", json=payload).status_code == 400

def test_login_with_wrong_password_returns_401(client):
    client.post("/api/v1/auth/register", json={"email": "b@apnasargam.com", "password": "password123"})
    response = client.post("/api/v1/auth/login", json={"email": "b@apnasargam.com", "password": "wrong-password"})
    assert response.status_code == 401

def test_login_error_does_not_reveal_whether_email_exists(client):
    client.post("/api/v1/auth/register", json={"email": "c@apnasargam.com", "password": "password123"})
    wrong_password = client.post("/api/v1/auth/login", json={"email": "c@apnasargam.com", "password": "nope"})
    unknown_email = client.post("/api/v1/auth/login", json={"email": "nobody@apnasargam.com", "password": "nope"})
    assert wrong_password.json() == unknown_email.json()

def test_projects_require_authentication(client):
    response = client.get("/api/v1/projects/")
    assert response.status_code in (401, 403)

def test_create_and_list_own_projects(client):
    headers = register_and_login(client)
    created = client.post("/api/v1/projects/", json=PROJECT, headers=headers)
    assert created.status_code == 200
    listed = client.get("/api/v1/projects/", headers=headers)
    assert [p["name"] for p in listed.json()] == ["Test Track"]

def test_users_only_see_their_own_projects(client):
    alice = register_and_login(client, "alice@apnasargam.com")
    bob = register_and_login(client, "bob@apnasargam.com")
    client.post("/api/v1/projects/", json=PROJECT, headers=alice)
    assert client.get("/api/v1/projects/", headers=bob).json() == []

def test_cannot_read_update_or_delete_another_users_project(client):
    alice = register_and_login(client, "alice@apnasargam.com")
    bob = register_and_login(client, "bob@apnasargam.com")
    project_id = client.post("/api/v1/projects/", json=PROJECT, headers=alice).json()["id"]

    assert client.get(f"/api/v1/projects/{project_id}", headers=bob).status_code == 403
    assert client.patch(f"/api/v1/projects/{project_id}", json={"bpm": 200}, headers=bob).status_code == 403
    assert client.delete(f"/api/v1/projects/{project_id}", headers=bob).status_code == 403

def test_missing_project_returns_404(client):
    headers = register_and_login(client)
    assert client.get("/api/v1/projects/9999", headers=headers).status_code == 404

def test_patch_only_changes_the_fields_that_were_sent(client):
    headers = register_and_login(client)
    project_id = client.post("/api/v1/projects/", json=PROJECT, headers=headers).json()["id"]

    updated = client.patch(f"/api/v1/projects/{project_id}", json={"bpm": 130}, headers=headers).json()

    assert updated["bpm"] == 130
    assert updated["name"] == "Test Track"
    assert updated["genre"] == "Jazz"
    assert updated["mood"] == "Calm"

def test_delete_removes_the_project(client):
    headers = register_and_login(client)
    project_id = client.post("/api/v1/projects/", json=PROJECT, headers=headers).json()["id"]

    assert client.delete(f"/api/v1/projects/{project_id}", headers=headers).status_code == 204
    assert client.get(f"/api/v1/projects/{project_id}", headers=headers).status_code == 404