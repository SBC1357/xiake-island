"""Integration test for knowledge-assets API endpoint proving Xiakedao consumer seam"""
import sys
import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Set the xiakedao consumer root BEFORE importing the app (Linux path)
os.environ['XIAGEDAO_CONSUMER_ROOT'] = '/root/.openclaw/workspace/huidu/cang/publish/current/consumers/xiakedao'

# Add xiakedao to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Reset the asset bridge singleton to pick up the new environment variable
from src.assembly import reset_asset_bridge
reset_asset_bridge()

from src.api.app import app


class TestKnowledgeAssetsAPI:
    """Test the /v1/workflow/knowledge-assets endpoint - proves Xiakedao consumer seam is wired"""
    
    @pytest.fixture
    def client(self):
        """Create a test client"""
        return TestClient(app)
    
    def test_knowledge_assets_returns_200(self, client):
        """Verify the endpoint is accessible"""
        response = client.get("/v1/workflow/knowledge-assets")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    def test_knowledge_assets_has_l2_true(self, client):
        """Verify the Xiakedao consumer seam provides L2 content"""
        response = client.get("/v1/workflow/knowledge-assets")
        data = response.json()
        
        # This proves the Xiakedao consumer seam is wired into a real request path
        assert data["has_l2"] is True, "Expected has_l2=True, proving xiakedao consumer has L2 content"
    
    def test_knowledge_assets_consumer_root_is_xiakedao(self, client):
        """Verify the consumer root points to xiakedao"""
        response = client.get("/v1/workflow/knowledge-assets")
        data = response.json()
        
        consumer_root = data.get("consumer_root", "")
        assert "xiakedao" in consumer_root.lower(), f"Expected xiakedao in consumer_root, got: {consumer_root}"
    
    def test_knowledge_assets_l2_files_exist(self, client):
        """Verify L2 files are returned from the xiakedao consumer"""
        response = client.get("/v1/workflow/knowledge-assets")
        data = response.json()
        
        l2_files = data.get("l2_files", [])
        assert len(l2_files) > 0, "Expected L2 files to be returned"
        
        # Check for expected medical_playbook files
        expected_files = ["m0_persona_templates.json", "m3_strategic_plays.json"]
        for expected in expected_files:
            assert any(expected in f for f in l2_files), f"Expected {expected} in l2_files"
    
    def test_knowledge_assets_consumer_count(self, client):
        """Verify consumer assets are being read from xiakedao"""
        response = client.get("/v1/workflow/knowledge-assets")
        data = response.json()
        
        consumer_count = data.get("consumer_assets_count", 0)
        assert consumer_count > 100, f"Expected > 100 consumer assets, got {consumer_count}"