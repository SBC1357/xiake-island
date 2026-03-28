"""Integration test for Xiakedao L3/L4 consumption"""
import sys
import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Set the xiakedao consumer root (Linux path)
os.environ['XIAGEDAO_CONSUMER_ROOT'] = '/root/.openclaw/workspace/huidu/cang/publish/current/consumers/xiakedao'

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.assembly import reset_asset_bridge
reset_asset_bridge()

from src.api.app import app


class TestXiakedaoL3L4:
    """Test Xiakedao can consume L3/L4 content"""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_knowledge_assets_has_l3(self, client):
        """Verify Xiakedao consumer has L3 content"""
        response = client.get("/v1/workflow/knowledge-assets")
        data = response.json()

        # Check if L3 directory exists in consumer root
        consumer_root = data.get("consumer_root", "")
        l3_path = Path(consumer_root) / "l3"
        has_l3 = l3_path.exists()
        assert has_l3, f"L3 directory should exist at {l3_path}"

    def test_knowledge_assets_has_l4(self, client):
        """Verify Xiakedao consumer has L4 content"""
        response = client.get("/v1/workflow/knowledge-assets")
        data = response.json()

        consumer_root = data.get("consumer_root", "")
        l4_path = Path(consumer_root) / "l4"
        has_l4 = l4_path.exists()
        assert has_l4, f"L4 directory should exist at {l4_path}"

    def test_l3_product_files_exist(self, client):
        """Verify L3 has disease knowledge files"""
        response = client.get("/v1/workflow/knowledge-assets")
        data = response.json()

        consumer_root = Path(data.get("consumer_root", ""))
        l3_path = consumer_root / "l3"

        if l3_path.exists():
            json_files = list(l3_path.rglob("*.json"))
            assert len(json_files) >= 10, f"Expected at least 10 L3 JSON files, got {len(json_files)}"

    def test_l4_product_files_exist(self, client):
        """Verify L4 has product manifest files"""
        response = client.get("/v1/workflow/knowledge-assets")
        data = response.json()

        consumer_root = Path(data.get("consumer_root", ""))
        l4_path = consumer_root / "l4"

        if l4_path.exists():
            # Check for product manifests
            products = ["lecanemab", "donanemab", "pluvicto", "furmonertinib", "lemborexant"]
            found_products = []
            for product in products:
                product_path = l4_path / product
                if product_path.exists():
                    json_files = list(product_path.glob("*.json"))
                    if json_files:
                        found_products.append(product)

            assert len(found_products) >= 5, f"Expected at least 5 products with manifests, got {len(found_products)}: {found_products}"