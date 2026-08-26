import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

TEST_USER = {
    "email": "test.pytest@example.com",
    "nom": "Rakoto",
    "prenom": "Jean",
    "mot_de_passe": "Password123!"
}


def test_1_register():
    """Vérifie l'inscription d'un utilisateur."""
    response = client.post("/api/auth/register", json=TEST_USER)
    assert response.status_code in [201, 400]  # 201 si créé, 400 si l'email existe déjà


def test_2_login():
    """Vérifie la connexion et la récupération du token JWT."""
    payload = {
        "email": TEST_USER["email"],
        "mot_de_passe": TEST_USER["mot_de_passe"]
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["token_type"].lower() == "bearer"


def test_3_get_me():
    """Vérifie la route protégée /me avec le token."""
    login_res = client.post("/api/auth/login", json={
        "email": TEST_USER["email"],
        "mot_de_passe": TEST_USER["mot_de_passe"]
    })
    token = login_res.json()["token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 200


def test_4_me_unauthorized():
    """Vérifie le rejet d'accès sans token."""
    response = client.get("/api/auth/me")
    assert response.status_code == 401