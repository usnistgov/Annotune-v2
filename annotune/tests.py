from django.test import LiveServerTestCase
from selenium import webdriver


class Hosttest(LiveServerTestCase):

    def testhomepage(self):
        driver = webdriver.Chrome()

        driver.get("http://127.0.0.1:8000/")
        assert "Fiifi" in driver.title



