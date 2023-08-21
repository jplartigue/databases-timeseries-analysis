
from django.test import TestCase
from rest_framework.test import APIClient


class TestViewRecherchePoint(TestCase):
    def test_tout_sur_rechercherpoint(self):
        client = APIClient()
        reponse = client.get('http://127.0.0.1:8000/benchmark/', format='json')