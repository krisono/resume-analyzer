from src.app_factory import create_app

def test_pdf_report_content_type():
    app = create_app()
    client = app.test_client()
    payload = {
        "resume_text": "Java developer with Spring Boot and Kafka.",
        "job_description_text": "Looking for Java engineer with Spring Boot and Kafka."
    }
    r = client.post("/api/report/pdf", json=payload)
    assert r.status_code == 200
    assert r.headers.get("Content-Type") == "application/pdf"
    assert len(r.data) > 1000  # bytes