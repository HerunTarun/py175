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

    def test_view_document(self):
        with self.client.get("/about.txt") as response:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content_type,
                             "text/plain; charset=utf-8")

            self.assertEqual(response.get_data(),
                         b"This is my file management application")

    def test_no_such_document(self):
        # verify redirect
        with self.client.get("/x9y5.ext") as response:
            self.assertEqual(response.status_code, 302)

        # send new GET and verify flash message
        with self.client.get(response.headers['Location']) as response:
            self.assertEqual(response.status_code, 200)
            self.assertIn("x9y5.ext does not exist",
                      response.get_data(as_text=True))

        # verify flash message has been consumed
        with self.client.get("/") as response:
            self.assertNotIn("x9y5.ext does not exist",
                      response.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()