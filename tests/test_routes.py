from src.app_factory import create_app

def test_health_route():
    app = create_app()
    client = app.test_client()
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"
    assert "ai" in r.get_json()

def test_analyze_without_key():
    app = create_app()
    client = app.test_client()
    payload = {
        "resume_text": "Experienced with Java, Spring Boot, Kafka.",
        "job_description_text": "Looking for Java developer with Spring Boot and Kafka experience."
    }
    r = client.post("/api/analyze", json=payload)
    data = r.get_json()
    assert r.status_code == 200
    assert data["ai"]["openai_enabled"] in (False, True)
    if not data["ai"]["openai_enabled"]:
        assert data["suggestions"] == []
    assert "section_alignment" in data["scores"]