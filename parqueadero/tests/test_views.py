from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from parqueadero.models import Entrada, Parqueadero, PerfilUsuario, Vehiculo


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

    def test_heading_responde_correctamente(self):
        response = self.client.get(reverse("heading"), {"eta": 20})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "parqueadero/heading.html")


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

    def test_profile_actualiza_datos_personales(self):
        self.client.login(username="maria", password="123456")
        response = self.client.post(
            reverse("profile"),
            {
                "action": "update_profile",
                "full_name": "Maria Gomez",
                "email": "maria@example.com",
                "telefono": "3001112233",
                "codigo_estudiantil": "202455",
                "tipo_usuario": "profesor",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        perfil = PerfilUsuario.objects.get(user=self.user)
        self.assertEqual(self.user.first_name, "Maria")
        self.assertEqual(self.user.last_name, "Gomez")
        self.assertEqual(perfil.telefono, "3001112233")
        self.assertEqual(perfil.tipo_usuario, "profesor")

    def test_profile_actualiza_vehiculo(self):
        self.client.login(username="maria", password="123456")
        response = self.client.post(
            reverse("profile"),
            {
                "action": "update_vehicle",
                "placa": "XYZ987",
                "marca": "Toyota",
                "modelo": "Corolla",
                "color": "Blanco",
                "tipo_vehiculo": "carro",
            },
        )
        self.assertEqual(response.status_code, 302)
        perfil = PerfilUsuario.objects.get(user=self.user)
        vehiculo = Vehiculo.objects.get(usuario=perfil)
        self.assertEqual(vehiculo.placa, "XYZ987")

    def test_profile_elimina_cuenta(self):
        self.client.login(username="maria", password="123456")
        response = self.client.post(reverse("profile"), {"action": "delete_account"})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(User.objects.filter(username="maria").exists())
