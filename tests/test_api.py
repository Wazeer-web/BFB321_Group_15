
"""Automated API validation tests for the Kopano dashboard."""

import unittest
from unittest.mock import patch

import app as app_module


class TestKopanoAPI(unittest.TestCase):

    def setUp(self):
        app_module.app.config["TESTING"] = True
        self.client = app_module.app.test_client()

    def test_invalid_product_pagination(self):
        response = self.client.get("/api/products?page=0")
        self.assertEqual(response.status_code, 400)

    def test_invalid_products_per_page(self):
        response = self.client.get("/api/products?per_page=101")
        self.assertEqual(response.status_code, 400)

    def test_product_creation_missing_required_fields(self):
        with patch.object(app_module, "get_db_connection") as mock_db:
            response = self.client.post(
                "/api/products",
                json={"product_name": "Test Product"}
            )
            self.assertEqual(response.status_code, 400)
            mock_db.assert_not_called()

    def test_product_creation_rejects_negative_stock(self):
        response = self.client.post(
            "/api/products",
            json={
                "supplier_id": 1,
                "product_name": "Test Product",
                "category": "Furniture",
                "sku": "TEST001",
                "unit_price": 100,
                "quantity_in_stock": -5,
                "reorder_level": 10
            }
        )
        self.assertEqual(response.status_code, 400)

    def test_product_creation_rejects_invalid_json(self):
        response = self.client.post(
            "/api/products",
            data="not valid json",
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_supplier_creation_requires_name(self):
        response = self.client.post(
            "/api/suppliers",
            json={"email": "test@example.com"}
        )
        self.assertEqual(response.status_code, 400)

    def test_delivery_rejects_invalid_date(self):
        response = self.client.post(
            "/api/deliveries",
            json={
                "supplier_id": 1,
                "delivery_reference": "TEST-001",
                "expected_date": "not-a-date"
            }
        )
        self.assertEqual(response.status_code, 400)

    def test_delivery_rejects_invalid_status(self):
        response = self.client.put(
            "/api/deliveries/1",
            json={"delivery_status": "Unknown"}
        )
        self.assertEqual(response.status_code, 400)

    def test_unknown_api_endpoint_returns_404(self):
        response = self.client.get("/api/unknown")
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.get_json())

    def test_wrong_http_method_returns_405(self):
        response = self.client.patch("/api/products")
        self.assertEqual(response.status_code, 405)
        self.assertIn("error", response.get_json())


if __name__ == "__main__":
    unittest.main()
