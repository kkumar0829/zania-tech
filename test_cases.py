import unittest
from io import BytesIO
from flask import Flask, json
from flask_restful import Api

from handler import UploadPdf, AskQuestion


class FlaskAppTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up a Flask test client for testing"""
        app = Flask(__name__)
        api = Api(app)
        app.testing = True
        api.add_resource(UploadPdf, '/v1/upload/')
        api.add_resource(AskQuestion, '/v1/ask/')
        cls.client = app.test_client()

    def test_upload_pdf_no_file(self):
        """Test /v1/upload with no file"""
        data = {'file': (BytesIO(b"fake file content"), '')}  # Change None to ''
        response = self.client.post('/v1/upload/', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.data), {"error": "No selected file"})

    def test_upload_pdf_invalid_file_type(self):
        """Test /v1/upload with a non-PDF file"""
        data = {'file': (BytesIO(b"fake file content"), 'test.txt')}
        response = self.client.post('/v1/upload/', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.data), {"error": "Invalid file type. Only PDF is supported."})

    def test_ask_question_no_questions(self):
        """Test /v1/ask with no questions provided"""
        response = self.client.post('/v1/ask/', data=json.dumps({}), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.data), {"error": "No questions provided"})

    def test_ask_question_with_questions(self):
        """Test /v1/ask with valid questions"""
        questions = {"questions": ["What is the summary of the document?"]}
        response = self.client.post('/v1/ask/', data=json.dumps(questions), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        # self.assertIn("message", json.loads(response.data).get("message"))
        self.assertEqual(json.loads(response.data).get("message"), "Questions answered and sent to Slack")
        self.assertIn("answers", json.loads(response.data))


if __name__ == '__main__':
    unittest.main()
