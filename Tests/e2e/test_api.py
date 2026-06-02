from fastapi.testclient import TestClient
from Backend.main import app


client = TestClient(app)

# =========================
# 1. SUCCESS CASE
# =========================

def test_analyze_repo_success():
    response = client.post("/analyze", json={
        "repo_url": "https://github.com/octocat/Hello-World"
    })

    assert response.status_code == 200

    data = response.json()

    assert "title" in data
    assert "summary" in data
    assert "quality_score" in data
    assert "status" in data
    assert "confidence" in data


# =========================
# 2. INVALID INPUT (GATEWAY GUARDRAIL)
# =========================

def test_analyze_repo_invalid_url():
    response = client.post("/analyze", json={
        "repo_url": "invalid-url"
    })

    # should fail validation OR return controlled error
    assert response.status_code in [400, 422]


# =========================
# 3. EMPTY INPUT SAFETY TEST
# =========================

def test_analyze_repo_empty_input():
    response = client.post("/analyze", json={})

    assert response.status_code in [400, 422]


# =========================
# 4. RESPONSE STRUCTURE SAFETY (GUARDRAIL CHECK)
# =========================

def test_response_structure_consistency():
    response = client.post("/analyze", json={
        "repo_url": "https://github.com/octocat/Hello-World"
    })

    data = response.json()

    # ensure no missing fields
    required_fields = [
        "title",
        "summary",
        "quality_score",
        "status",
        "confidence",
        "review_feedback"
    ]

    for field in required_fields:
        assert field in data