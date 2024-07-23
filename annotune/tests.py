from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, mock_open
import json
import datetime
from django.utils.timezone import make_aware
from collections import OrderedDict
import environ
from django.conf import settings

env = environ.Env()

class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_data = {
            "first_name": "Test",
            "last_name": "User",
            "user_id": 0,
            "email": "danystevo@gmail.com",
            "password": "12345",
            "document_id": [],
            "label": [],
            "labels": {},
            "start_time": datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S"),
            "date": datetime.datetime.now().strftime("%d/%m/%y"),
            "pageTimes": [],
            "hoverTimes": []
        }
        self.mock_users = {"danystevo@gmail.com": self.user_data}
        self.test_document_id = 1
        self.test_label = 'test_label'
        self.test_hover_time = 10

        self.users_json_path = env("USERS_PATH")
        self.datapath = env("DATAPATH")
        self.url = env("URL")

        # Patch opening JSON files
        self.patcher = patch('builtins.open', mock_open(read_data=json.dumps(self.mock_users)))
        self.mock_open = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    # def test_sign_up_view(self):
    #     response = self.client.post(reverse('sign-up'), {
    #         'first_name': 'Test',
    #         'last_name': 'User',
    #         'email': 'testuser2@gmail.com',
    #         'password': '12345'
    #     })
    #     self.assertEqual(response.status_code, 302)  # Redirect to homepage

    # def test_login_view(self):
    #     response = self.client.post(reverse('login'), {
    #         'email': 'danystevo@gmail.com',
    #         'password': '12345'
    #     })
    #     self.assertEqual(response.status_code, 302)  # Redirect to homepage

    # def test_homepage_view(self):
    #     with patch('django.contrib.sessions.backends.db.SessionStore') as MockSession:
    #         session = MockSession()
    #         session["user_id"] = self.user_data["user_id"]
    #         session["email"] = self.user_data["email"]
    #         session["start_time"] = self.user_data["start_time"]
    #         session.save()
    #         self.client.cookies[settings.SESSION_COOKIE_NAME] = session.session_key

    #         response = self.client.get(reverse('homepage', args=[self.user_data["user_id"]]))
    #         self.assertEqual(response.status_code, 200)


    # @patch('requests.post')
    # def test_list_documents_view(self, mock_post):
    #     # Mock the external API call
    #     mock_response = {
    #         "document_id": self.test_document_id,
    #         "keywords": {"1": ["keyword1"], "2": ["keyword2"]},
    #         "cluster": {"1": [1, 2, 3], "2": [4, 5, 6]}
    #     }
    #     mock_post.return_value.json.return_value = mock_response

    #     # Ensure the session is correctly set up
    #     session = self.client.session
    #     session["user_id"] = self.user_data["user_id"]
    #     session["email"] = self.user_data["email"]
    #     session["start_time"] = self.user_data["start_time"]
    #     session.save()

    #     # Make the GET request
    #     response = self.client.get(reverse('documents', args=[self.user_data["user_id"]]))


    #     # Check the response status code
    #     self.assertEqual(response.status_code, 200)

    #     # Check if the keywords and topics are in the response content
    #     self.assertContains(response, "1")
    #     self.assertContains(response, "2")

    def test_label_view(self):
        with patch('django.contrib.sessions.backends.db.SessionStore') as MockSession:
            session = MockSession()
            session["user_id"] = self.user_data["user_id"]
            session["email"] = self.user_data["email"]
            session["start_time"] = self.user_data["start_time"]
            session.save()
            self.client.cookies[settings.SESSION_COOKIE_NAME] = session.session_key

            response = self.client.get(reverse('label', args=[self.user_data["user_id"], self.test_document_id]))
            self.assertEqual(response.status_code, 200)

    # def test_skip_document_view(self):
    #     response = self.client.post(reverse('skip_document'), {'current_doc_id': self.test_document_id})
    #     self.assertEqual(response.status_code, 200)

    # def test_submit_data_view(self):
    #     response = self.client.post(reverse('submit_data', args=[self.test_document_id, self.test_label]))
    #     self.assertEqual(response.status_code, 200)

    # def test_fetch_data_view(self):
    #     response = self.client.get(reverse('fetch_data', args=[self.user_data["user_id"], self.test_document_id]))
    #     self.assertEqual(response.status_code, 200)

    # def test_logout_view(self):
    #     with patch('django.contrib.sessions.backends.db.SessionStore') as MockSession:
    #         session = MockSession()
    #         session["user_id"] = self.user_data["user_id"]
    #         session["email"] = self.user_data["email"]
    #         session["start_time"] = self.user_data["start_time"]
    #         session.save()
    #         self.client.cookies[settings.SESSION_COOKIE_NAME] = session.session_key

    #         response = self.client.get(reverse('logout'))
    #         self.assertEqual(response.status_code, 302)  # Redirect to login

    # def test_append_time_view(self):
    #     response = self.client.post(reverse('append_time', args=['test_page']))
    #     self.assertEqual(response.status_code, 200)

    # def test_display_view(self):
    #     with patch('django.contrib.sessions.backends.db.SessionStore') as MockSession:
    #         session = MockSession()
    #         session["user_id"] = self.user_data["user_id"]
    #         session["email"] = self.user_data["email"]
    #         session["start_time"] = self.user_data["start_time"]
    #         session.save()
    #         self.client.cookies[settings.SESSION_COOKIE_NAME] = session.session_key

    #         response = self.client.get(reverse('display', args=[self.user_data["user_id"]]))
    #         self.assertEqual(response.status_code, 200)

    # def test_relabel_view(self):
    #     response = self.client.get(reverse('relabel', args=[self.test_document_id, self.test_label]))
    #     self.assertEqual(response.status_code, 200)

    # def test_log_hover_view(self):
    #     response = self.client.post(reverse('log_hover', args=[self.test_document_id, self.test_hover_time]))
    #     self.assertEqual(response.status_code, 200)
