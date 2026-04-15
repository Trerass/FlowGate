from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from parqueadero.models import Entrada, Parqueadero, PerfilUsuario


class PublicViewsTests(TestCase):
    def setUp(self):
        parqueadero = Parqueadero.objects.create(nombre="Principal", capacidad=100)
        Entrada.objects.create(nombre="Norte", parqueadero=parqueadero)

    def test_home_responde_correctamente(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "parqueadero/home.html")

    def test_payments_responde_correctamente(self):
        response = self.client.get(reverse("payments"), {"amount": 5000})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "5000")


class AuthenticatedViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="maria", password="123456")
        PerfilUsuario.objects.create(user=self.user)

    def test_profile_requiere_autenticacion(self):
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 302)

    def test_profile_autenticado_responde_correctamente(self):
        self.client.login(username="maria", password="123456")
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "parqueadero/profile.html")
