import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestHealthCheck:
    """Test suite for the health check endpoint."""
    
    def test_health_check_returns_200_and_healthy_status(self):
        """
        GIVEN a running FastAPI application
        WHEN the /health endpoint is called with GET
        THEN it should return a 200 status code and {status: 'healthy'}
        """
        # When
        response = client.get("/health")
        
        # Then
        assert response.status_code == 200, "Status code should be 200"
        assert response.json() == {"status": "healthy"}, "Response should be {'status': 'healthy'}"
        print("✓ Health check returns 200 and healthy status")

    def test_cors_headers_are_set_correctly(self):
        """
        GIVEN a running FastAPI application with CORS enabled
        WHEN an OPTIONS request is made to /health with CORS headers
        THEN it should return the appropriate CORS headers
        """
        # When
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "*"
            }
        )
        
        # Then
        assert response.status_code == 200, "Status code should be 200 for OPTIONS"
        assert response.headers["access-control-allow-origin"] == "http://localhost:3000", \
            "CORS origin should be allowed"
        assert "access-control-allow-methods" in response.headers, \
            "CORS methods should be specified"
        assert "access-control-allow-headers" in response.headers, \
            "CORS headers should be allowed"
        assert response.headers["access-control-allow-credentials"] == "true", \
            "CORS credentials should be allowed"
        print("✓ CORS headers are correctly set")

    def test_post_method_not_allowed(self):
        """
        GIVEN a running FastAPI application
        WHEN the /health endpoint is called with POST
        THEN it should return 405 Method Not Allowed
        """
        # When
        response = client.post("/health")
        
        # Then
        assert response.status_code == 405, "Status code should be 405 for POST"
        print("✓ POST method is correctly not allowed")

# This allows running the tests with `python -m pytest tests/test_main.py -v`
if __name__ == "__main__":
    pytest.main(["-v"])
