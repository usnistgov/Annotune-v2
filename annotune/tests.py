from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, mock_open
import json
import datetime
from django.conf import settings
from django.test import LiveServerTestCase
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import json
import environ

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

    def test_sign_up_view(self):
        response = self.client.post(reverse('sign-up'), {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser2@gmail.com',
            'password': '12345'
        })
        self.assertEqual(response.status_code, 302)  # Redirect to homepage

    def test_login_view(self):
        response = self.client.post(reverse('login'), {
            'email': 'danystevo@gmail.com',
            'password': '12345'
        })
        self.assertEqual(response.status_code, 302)  # Redirect to homepage

    def test_homepage_view(self):
        with patch('django.contrib.sessions.backends.db.SessionStore') as MockSession:
            session = MockSession()
            session["user_id"] = self.user_data["user_id"]
            session["email"] = self.user_data["email"]
            session["start_time"] = self.user_data["start_time"]
            session.save()
            self.client.cookies[settings.SESSION_COOKIE_NAME] = session.session_key

            response = self.client.get(reverse('homepage', args=[self.user_data["user_id"]]))
            self.assertEqual(response.status_code, 200)
            
    def perform_request(self, user_id, document_id):
        # Make a request to the label view
        url = self.live_server_url + reverse('label', args=[user_id, document_id])
        session = requests.Session()
        session.cookies.set('sessionid', self.client.cookies['sessionid'])

        response = session.get(url)
        return response

    def test_load_label_view(self):
        user_id = self.user_data["user_id"]
        document_id = self.test_document_id

        # Set up session cookies
        self.client.post(reverse('login'), {
            'email': 'danystevo@gmail.com',
            'password': '12345'
        })

        # Define number of concurrent requests
        num_requests = 50

        with ThreadPoolExecutor(max_workers=num_requests) as executor:
            future_to_request = {executor.submit(self.perform_request, user_id, document_id): i for i in range(num_requests)}

            for future in as_completed(future_to_request):
                try:
                    response = future.result()
                    self.assertEqual(response.status_code, 200)
                except Exception as exc:
                    print(f'Generated an exception: {exc}')

