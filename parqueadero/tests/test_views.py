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
        self.assertContains(response, "Tarifas de Parqueadero")
        self.assertContains(response, "Personal - Automovil")
        self.assertNotContains(response, "Monto a recargar")
        self.assertNotContains(response, "Historial")

    def test_heading_requiere_autenticacion(self):
        response = self.client.get(reverse("heading"), {"eta": 20})
        self.assertEqual(response.status_code, 302)

    def test_menu_publico_oculta_opciones_de_usuario_registrado(self):
        response = self.client.get(reverse("home"))
        self.assertNotContains(response, "En Camino")
        self.assertNotContains(response, "Perfil")

    def test_home_muestra_lleno_cuando_ocupancia_iguala_capacidad(self):
        Parqueadero.objects.update(capacidad=80, ocupancia=80)
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Lleno")
        self.assertContains(response, 'data-count="80"')
        self.assertContains(response, "/80")


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

    def test_profile_profesor_muestra_codigo_de_profesor(self):
        PerfilUsuario.objects.filter(user=self.user).update(tipo_usuario="profesor")
        self.client.login(username="maria", password="123456")
        response = self.client.get(reverse("profile"))
        self.assertContains(response, "Codigo de Profesor")
        self.assertNotContains(response, "Codigo Estudiantil:")

    def test_profile_trabajador_muestra_codigo_de_trabajador(self):
        PerfilUsuario.objects.filter(user=self.user).update(tipo_usuario="trabajador")
        self.client.login(username="maria", password="123456")
        response = self.client.get(reverse("profile"))
        self.assertContains(response, "Codigo de Trabajador")
        self.assertContains(response, "Trabajador")

    def test_profile_admin_no_muestra_codigo_ni_tipo_usuario(self):
        admin = User.objects.create_user(username="admin", password="123456", is_staff=True)
        self.client.login(username="admin", password="123456")
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Codigo")
        self.assertNotContains(response, "Tipo de Usuario")
        self.assertTrue(PerfilUsuario.objects.filter(user=admin).exists())

    def test_heading_autenticado_responde_correctamente(self):
        self.client.login(username="maria", password="123456")
        response = self.client.get(reverse("heading"), {"eta": 20})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "parqueadero/heading.html")

    def test_payments_autenticado_muestra_funciones_de_pago(self):
        self.client.login(username="maria", password="123456")
        response = self.client.get(reverse("payments"), {"amount": 5000})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Personal - Automovil")
        self.assertContains(response, "Monto a recargar")
        self.assertContains(response, "5000")
        self.assertContains(response, "Historial")

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

    def test_profile_actualiza_tipo_usuario_a_trabajador(self):
        self.client.login(username="maria", password="123456")
        response = self.client.post(
            reverse("profile"),
            {
                "action": "update_profile",
                "full_name": "Maria Gomez",
                "email": "maria@example.com",
                "telefono": "3001112233",
                "codigo_estudiantil": "TRB-01",
                "tipo_usuario": "trabajador",
            },
        )
        self.assertEqual(response.status_code, 302)
        perfil = PerfilUsuario.objects.get(user=self.user)
        self.assertEqual(perfil.tipo_usuario, "trabajador")
        self.assertEqual(perfil.codigo_estudiantil, "TRB-01")

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


class AdminPanelTests(TestCase):
    def setUp(self):
        self.parqueadero = Parqueadero.objects.create(nombre="Norte", capacidad=100, ocupancia=30)
        self.user = User.objects.create_user(username="usuario", password="123456")
        self.staff = User.objects.create_user(username="staff", password="123456", is_staff=True)
        self.superuser = User.objects.create_superuser(username="super", password="123456")

    def test_admin_panel_requiere_autenticacion(self):
        response = self.client.get(reverse("admin_panel"))
        self.assertEqual(response.status_code, 302)

    def test_admin_panel_bloquea_usuario_normal(self):
        self.client.login(username="usuario", password="123456")
        response = self.client.get(reverse("admin_panel"))
        self.assertEqual(response.status_code, 302)

    def test_admin_panel_permite_staff(self):
        self.client.login(username="staff", password="123456")
        response = self.client.get(reverse("admin_panel"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Panel administrativo")
        self.assertNotContains(response, "Crear administrador")

    def test_admin_actualiza_disponibilidad_en_base_de_datos(self):
        self.client.login(username="staff", password="123456")
        response = self.client.post(
            reverse("admin_panel"),
            {
                "action": "update_availability",
                f"capacidad_{self.parqueadero.id}": "120",
                f"ocupancia_{self.parqueadero.id}": "45",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.parqueadero.refresh_from_db()
        self.assertEqual(self.parqueadero.capacidad, 120)
        self.assertEqual(self.parqueadero.ocupancia, 45)

    def test_usuario_normal_no_actualiza_disponibilidad(self):
        self.client.login(username="usuario", password="123456")
        response = self.client.post(
            reverse("admin_panel"),
            {
                "action": "update_availability",
                f"capacidad_{self.parqueadero.id}": "120",
                f"ocupancia_{self.parqueadero.id}": "45",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.parqueadero.refresh_from_db()
        self.assertEqual(self.parqueadero.capacidad, 100)
        self.assertEqual(self.parqueadero.ocupancia, 30)

    def test_superusuario_no_ve_creacion_de_administradores(self):
        self.client.login(username="super", password="123456")
        response = self.client.get(reverse("admin_panel"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Crear administrador")

    def test_panel_no_crea_administradores(self):
        self.client.login(username="super", password="123456")
        response = self.client.post(
            reverse("admin_panel"),
            {
                "action": "create_admin",
                "username": "nuevoadmin",
                "email": "admin@example.com",
                "password": "segura123",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="nuevoadmin").exists())
