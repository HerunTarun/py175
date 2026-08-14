import unittest
import shutil
import os
from app import app

class TestApp(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.data_path = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(self.data_path, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.data_path, ignore_errors=True)

    def create_document(self, name, content=""):
        with open(os.path.join(self.data_path, name), "w") as file:
            file.write(content)

    def test_view_index_page(self):
        self.create_document("about.txt")
        self.create_document("changes.txt")
        self.create_document("history.txt")

        response = self.client.get("/")

        # verify status code and content type
        self.assertEqual(200, response.status_code)
        self.assertEqual("text/html; charset=utf-8", response.content_type)

        # verify contents
        self.assertIn("about.txt", response.get_data(as_text=True))
        self.assertIn("changes.txt", response.get_data(as_text=True))
        self.assertIn("history.txt", response.get_data(as_text=True))

    def test_view_document(self):
        self.create_document("about.txt",
                             content="This is my file management application.")

        with self.client.get("/about.txt") as response:
            # verify status code and content type
            self.assertEqual(200, response.status_code)
            self.assertEqual("text/plain; charset=utf-8",
                             response.content_type)

            # verify contents
            self.assertEqual(b"This is my file management application.",
                             response.get_data())

    def test_no_such_document(self):
        # verify redirect
        with self.client.get("/x9y5.ext") as response:
            self.assertEqual(302, response.status_code)

        # verify flash message
        with self.client.get(response.headers['Location']) as response:
            self.assertEqual(200, response.status_code)
            self.assertIn("x9y5.ext does not exist",
                      response.get_data(as_text=True))

        # verify flash message has been consumed
        with self.client.get("/") as response:
            self.assertNotIn("x9y5.ext does not exist",
                      response.get_data(as_text=True))

    def test_markdown_files(self):
        self.create_document("markdown.md",
                             content="A dynamic <em>open source</em>")

        with self.client.get("/markdown.md") as response:
            # verify status code and content type
            self.assertEqual(200, response.status_code)
            self.assertEqual("text/html; charset=utf-8", response.content_type)

            # verify contents
            self.assertIn("A dynamic <em>open source</em>",
                          response.get_data(as_text=True))

    def test_view_edit_document_page(self):
        self.create_document("history.txt")

        response = self.client.get("/history.txt/edit")

        # verify status code of edit button and content type
        self.assertEqual(200, response.status_code)
        self.assertEqual("text/html; charset=utf-8", response.content_type)

        # verify text area contents
        self.assertIn("<textarea", response.get_data(as_text=True))

    def test_update_document(self):
        self.create_document("history.txt", content="some history")

        response = self.client.post("/history.txt",
                                    data={'content': "new content"})

        # verify redirect after save changes
        self.assertEqual(302, response.status_code)

        # verify new contents of document
        with self.client.get("/history.txt") as contents:
            self.assertIn("new content", contents.get_data(as_text=True))

        # verify flash message
        with self.client.get(response.headers['Location']) as response:
            self.assertEqual(200, response.status_code)
            self.assertIn("history.txt has been updated",
                             response.get_data(as_text=True))

        # verify flash message has been consumed
        with self.client.get('/') as response:
            self.assertNotIn("history.txt has been updated.",
                             response.get_data(as_text=True))

    def test_view_new_document_page(self):
        response = self.client.get("/new")

        # verify status code and content type
        self.assertEqual(200, response.status_code)
        self.assertEqual("text/html; charset=utf-8", response.content_type)

        # verify contents
        self.assertIn("<input name", response.get_data(as_text=True))
        self.assertIn("<button type=", response.get_data(as_text=True))

    def test_create_document_success(self):
        response = self.client.post("/new",
                                    data={ "document_name": "testing.txt"})

        # verify redirect
        self.assertEqual(302, response.status_code)

        # verify whether file exists
        file_path = os.path.join(self.data_path, "testing.txt")
        self.assertTrue(os.path.exists(file_path))

        # verify flash message
        with self.client.get(response.headers['Location']) as responses:
            self.assertEqual(200, responses.status_code)
            self.assertIn("testing.txt has been created.",
                          responses.get_data(as_text=True))

        # verify flash message has been consumed
        with self.client.get('/') as response:
            self.assertNotIn("testing.txt has been created.",
                             response.get_data(as_text=True))

    def test_create_document_when_document_already_exists(self):
        self.create_document("testing.txt")

        response = self.client.post("/new",
                                    data={ "document_name": "testing.txt"})

        # verify status code
        self.assertEqual(422, response.status_code)

        # verify flash message
        self.assertIn("testing.txt already exists.",
                      response.get_data(as_text=True))

        # verify flash message has been consumed
        with self.client.get("/new") as response:
            self.assertNotIn("testing.txt already exists.",
                            response.get_data(as_text=True))

    def test_create_document_without_name(self):
        response = self.client.post("/new",
                                    data={ "document_name": ""})

        # verify status code
        self.assertEqual(422, response.status_code)

        # verify flash message
        self.assertIn("A name is required.", response.get_data(as_text=True))

        # verify flash message has been consumed
        with self.client.get("/new") as response:
            self.assertNotIn("A name is required.",
                            response.get_data(as_text=True))

    def test_delete_file_success(self):
        self.create_document("delete_this.txt")

        response = self.client.post("/delete_this.txt/delete",
                                    follow_redirects=True)

        # verify status code
        self.assertEqual(200, response.status_code)

        # verify file deleted
        deleted_file_path = os.path.join(self.data_path, "delete_this.txt")
        self.assertFalse(os.path.exists(deleted_file_path))

        # verify flash message
        self.assertIn("delete_this.txt has been deleted.",
                      response.get_data(as_text=True))

        # verify flash message has been consumed
        with self.client.get("/") as response:
            self.assertNotIn("delete_this.txt has been deleted.",
                      response.get_data(as_text=True))

    def test_delete_file_when_nonexistent_file(self):
        response = self.client.post("/delete_this.txt/delete",
                                    follow_redirects=True)

        # verify status code
        self.assertEqual(200, response.status_code)

        # verify flash message
        self.assertIn("delete_this.txt does not exist.",
                      response.get_data(as_text=True))

        # verify flash message has been consumed
        with self.client.get("/") as response:
            self.assertNotIn("delete_this.txt does not exist.",
                      response.get_data(as_text=True))

    def test_view_login_page(self):
        response = self.client.get("/login")

        # verify status code
        self.assertEqual(200, response.status_code)

        # verify contents
        self.assertIn("<label class=\"login\"",
                      response.get_data(as_text=True))

    def test_login_form_valid_credentials(self):
        response = self.client.post("/login",
                                    data={ "username": "admin",
                                          "password": "secret3"},
                                    follow_redirects=True)

        # verify status code and contents
        self.assertEqual(200, response.status_code)
        self.assertIn("Signed in as admin", response.get_data(as_text=True))

        # verify flash message
        self.assertIn("Welcome!", response.get_data(as_text=True))

        # verify flash message consumed
        with self.client.get("/") as response:
            self.assertNotIn("Welcome!", response.get_data(as_text=True))

    def test_login_form_valid_user_invalid_password(self):
        response = self.client.post("/login",
                                    data={ "username": "admin",
                                          "password": "jacob"})

        # verify status code and contents
        self.assertEqual(200, response.status_code)
        self.assertIn("admin", response.get_data(as_text=True))

        # verify flash message
        self.assertIn("Invalid password", response.get_data(as_text=True))

        # verify flash message consumed
        with self.client.get("/login") as response:
            self.assertNotIn("Invalid password",
                             response.get_data(as_text=True))


    def test_login_form_invalid_credentials(self):
        response = self.client.post("/login",
                                    data={ "username": "john",
                                          "password": "jacob"})

        # verify status code and contents
        self.assertEqual(200, response.status_code)

        # verify flash message
        self.assertIn("john does not exist.", response.get_data(as_text=True))

        # verify flash message consumed
        with self.client.get("/login") as response:
            self.assertNotIn("john does not exist.",
                             response.get_data(as_text=True))

    def test_logout_form(self):
        self.client.post("/login",
                         data={ "username": "admin",
                               "password": "secret3"},
                         follow_redirects=True)

        response = self.client.post("/admin/logout", follow_redirects=True)

        # verify status code and contents
        self.assertEqual(200, response.status_code)
        self.assertIn("log in", response.get_data(as_text=True))

        # verify flash message
        self.assertIn("You have been logged out.", response.get_data(as_text=True))

        # verify flash message consumed
        with self.client.get("/") as response:
            self.assertNotIn("You have been logged out.",
                             response.get_data(as_text=True))



if __name__ == "__main__":
    unittest.main()