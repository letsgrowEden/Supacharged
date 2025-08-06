import pytest
from fastapi.testclient import TestClient
from db.db import supabase_client
from main import app

client = TestClient(app)

class TestDatabaseConnection:
    """Test suite for database connection and operations."""
    
    def test_database_connection(self):
        """
        GIVEN a configured Supabase client
        WHEN we attempt to connect to the database
        THEN the connection should be successful
        """
        try:
            # Test the connection by making a simple query
            response = supabase_client.table('design_kits').select('*').limit(1).execute()
            assert response is not None, "Database response should not be None"
            assert hasattr(response, 'data'), "Response should have a data attribute"
            print("✓ Successfully connected to Supabase database")
            
        except Exception as e:
            pytest.fail(f"Failed to connect to Supabase: {str(e)}")

    def test_health_check_with_db(self):
        """
        GIVEN a running FastAPI application with database connection
        WHEN the /health endpoint is called
        THEN it should return a 200 status and a detailed health status
        """
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["environment"] == "configured"
        
        db_health = data["database"]
        assert db_health["status"] == "connected"
        assert db_health["can_query"] is True
        print("✓ Health check reports database status: connected")
