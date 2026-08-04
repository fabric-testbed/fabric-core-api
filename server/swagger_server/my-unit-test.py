# my-unit-tests.py - Professional unit tests for people_controller.py (do not commit hardcoded values)
import unittest
from unittest.mock import MagicMock, patch
import os
from flask.testing import FlaskClient
from swagger_server.__main__ import app  # Import your Flask app instance


class TestPeopleController(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        # Load test token from env (never hardcode!)
        self.TEST_TOKEN = os.getenv("TEST_API_TOKEN", "test_token_123")
        # Mock the actual API call dependency
        self.mock_api = MagicMock()

    @patch('swagger_server.controllers.people_controller.api_client')
    def test_get_people_success(self, mock_api):
        """Test successful people retrieval with valid token"""
        mock_api.get.return_value.json.return_value = [{"id": 1, "name": "John Doe"}]

        response = self.app.get(
            '/api/people',
            headers={"Authorization": f"Bearer {self.TEST_TOKEN}"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("John Doe", str(response.data))

    @patch('swagger_server.controllers.people_controller.api_client')
    def test_get_people_unauthorized(self, mock_api):
        """Test unauthorized access (missing token)"""
        response = self.app.get('/api/people')

        self.assertEqual(response.status_code, 401)
        self.assertIn("Unauthorized", str(response.data))

    @patch('swagger_server.controllers.people_controller.api_client')
    def test_get_people_invalid_token(self, mock_api):
        """Test invalid token rejection"""
        response = self.app.get(
            '/api/people',
            headers={"Authorization": "Bearer INVALID_TOKEN"}
        )

        self.assertEqual(response.status_code, 401)
        self.assertIn("Invalid token", str(response.data))


if __name__ == '__main__':
    unittest.main()
