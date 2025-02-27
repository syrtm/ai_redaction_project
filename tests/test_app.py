import unittest
from app import app

class FlaskAppTests(unittest.TestCase):
    def setUp(self):
        from app import app  # Eğer app modülünü import etmediyseniz
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.app.testing = True

    def test_home(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"API is running", response.data)

    def test_health(self):
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"healthy", response.data)

    def test_mask_endpoint_no_text(self):
        response = self.app.post('/mask', json={})
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"No text provided", response.data)

    def test_mask_endpoint_valid_text(self):
        response = self.app.post('/mask', json={"text": "My email is test@example.com", "mode": "partial"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"masked_text", response.data)

    def test_mask_endpoint_with_details(self):
        response = self.app.post('/mask', json={"text": "My email is test@example.com", "mode": "full", "return_details": True})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"details", response.data)

if __name__ == '__main__':
    unittest.main()
