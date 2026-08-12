import unittest
from app import app

class TestApp(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_index(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "text/html; charset=utf-8")

        self.assertIn("about.txt", response.get_data(as_text=True))
        self.assertIn("changes.txt", response.get_data(as_text=True))
        self.assertIn("history.txt", response.get_data(as_text=True))


    def test_document(self):
        with self.client.get("/about.txt") as response:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content_type,
                             "text/plain; charset=utf-8")

            self.assertEqual(response.get_data(),
                         b"This is my file management application")

if __name__ == "__main__":
    unittest.main()