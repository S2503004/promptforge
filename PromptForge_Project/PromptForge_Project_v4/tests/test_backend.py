
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_templates():
    r = client.get("/templates")
    assert r.status_code == 200
    assert "templates" in r.json()

def test_generate():
    payload = {"template_id": "summarize_v1", "variables": {"text": "hello world", "tone":"neutral","length":20}}
    r = client.post("/generate", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "prompt" in data and "model_output" in data
