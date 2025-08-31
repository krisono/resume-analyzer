from src.services.scoring_service import keyword_coverage

def test_keyword_coverage_basic():
    resume = "I worked with Java, Spring Boot, and Kafka at scale."
    kws = ["java", "spring boot", "kafka", "python"]
    coverage, missing, score = keyword_coverage(resume, kws)
    assert "python" in missing
    assert score > 60