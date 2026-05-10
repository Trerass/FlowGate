from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from parqueadero.models import (
    AvisoEnCamino,
    Entrada,
    MetodoPago,
    Parqueadero,
    PerfilUsuario,
    Vehiculo,
)


@override_settings(FLOWGATE_WEATHER_API_ENABLED=False)
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
        self.assertContains(response, "Tarifas de parqueadero")
        self.assertContains(response, "Personal - Automovil")
        self.assertNotContains(response, "Monto a recargar")
        self.assertNotContains(response, "Numero de tarjeta")
        self.assertNotContains(response, "Historial")

    def test_payments_post_publico_redirige_a_login(self):
        response = self.client.post(
            reverse("payments"),
            {
                "action": "save_card",
                "card_number": "4111 1111 1111 1111",
                "expiry": "12/30",
                "cvv": "123",
                "card_name": "Visitante",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login_view"), response["Location"])
        self.assertFalse(MetodoPago.objects.exists())

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

    def test_home_usa_fila_guardada_en_base_de_datos(self):
        Entrada.objects.filter(nombre="Norte").update(fila=9)
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-count="9"')

    def test_home_publico_oculta_parqueadero_de_profesores(self):
        response = self.client.get(reverse("home"))
        self.assertNotContains(response, "Profesores")

@override_settings(FLOWGATE_WEATHER_API_ENABLED=False)
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
        self.assertContains(response, "Codigo de profesor")
        self.assertNotContains(response, "Codigo estudiantil:")

    def test_profile_trabajador_muestra_codigo_de_trabajador(self):
        PerfilUsuario.objects.filter(user=self.user).update(tipo_usuario="trabajador")
        self.client.login(username="maria", password="123456")
        response = self.client.get(reverse("profile"))
        self.assertContains(response, "Codigo de trabajador")
        self.assertContains(response, "Trabajador")

    def test_profile_admin_no_muestra_codigo_ni_tipo_usuario(self):
        admin = User.objects.create_user(username="admin", password="123456", is_staff=True)
        self.client.login(username="admin", password="123456")
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Codigo")
        self.assertNotContains(response, "Tipo de usuario")
        self.assertTrue(PerfilUsuario.objects.filter(user=admin).exists())

    def test_heading_autenticado_responde_correctamente(self):
        self.client.login(username="maria", password="123456")
        response = self.client.get(reverse("heading"), {"eta": 20})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "parqueadero/heading.html")

    def test_heading_slider_usa_incrementos_de_un_minuto(self):
        self.client.login(username="maria", password="123456")
        response = self.client.get(reverse("heading"), {"eta": 1})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'min="1"')
        self.assertContains(response, 'max="60"')
        self.assertContains(response, 'step="1"')
        self.assertContains(response, 'value="1"')
        self.assertContains(response, "oninput=")
        self.assertContains(response, "data-eta-value")

    def test_heading_muestra_parqueaderos_y_entradas_para_seleccionar(self):
        parqueadero = Parqueadero.objects.create(nombre="Visitantes", capacidad=40)
        entrada = Entrada.objects.create(nombre="Principal (Visitantes)", parqueadero=parqueadero, fila=2)
        self.client.login(username="maria", password="123456")
        response = self.client.get(reverse("heading"))
        self.assertContains(response, 'name="parking"')
        self.assertContains(response, f'value="{parqueadero.id}"')
        self.assertContains(response, 'name="entrada"')
        self.assertContains(response, f'value="{entrada.id}"')
        self.assertContains(response, "Principal")

    def test_heading_crea_aviso_en_camino(self):
        parqueadero = Parqueadero.objects.create(nombre="Visitantes", capacidad=40)
        entrada = Entrada.objects.create(nombre="Principal (Visitantes)", parqueadero=parqueadero, fila=2)
        self.client.login(username="maria", password="123456")
        response = self.client.post(
            reverse("heading"),
            {
                "parking": str(parqueadero.id),
                "entrada": str(entrada.id),
                "eta": "10",
            },
        )
        self.assertEqual(response.status_code, 302)
        aviso = AvisoEnCamino.objects.get(entrada=entrada)
        self.assertEqual(aviso.eta_minutos, 10)
        self.assertFalse(aviso.agregado_a_fila)
        response = self.client.get(reverse("heading"))
        self.assertContains(response, "Viaje inicializado")
        self.assertContains(response, "Visitantes")
        self.assertContains(response, "Entrada Principal")
        self.assertContains(response, "Cancelar viaje")

    def test_heading_crea_aviso_con_eta_de_un_minuto(self):
        parqueadero = Parqueadero.objects.create(nombre="Visitantes", capacidad=40)
        entrada = Entrada.objects.create(nombre="Principal (Visitantes)", parqueadero=parqueadero, fila=2)
        self.client.login(username="maria", password="123456")
        response = self.client.post(
            reverse("heading"),
            {
                "parking": str(parqueadero.id),
                "entrada": str(entrada.id),
                "eta": "1",
            },
        )
        self.assertEqual(response.status_code, 302)
        aviso = AvisoEnCamino.objects.get(entrada=entrada)
        self.assertEqual(aviso.eta_minutos, 1)

    def test_heading_cancela_viaje_activo(self):
        parqueadero = Parqueadero.objects.create(nombre="Visitantes", capacidad=40)
        entrada = Entrada.objects.create(nombre="Principal (Visitantes)", parqueadero=parqueadero, fila=2)
        perfil = PerfilUsuario.objects.get(user=self.user)
        aviso = AvisoEnCamino.objects.create(
            usuario=perfil,
            parqueadero=parqueadero,
            entrada=entrada,
            eta_minutos=10,
            llegada_estimada=timezone.now() + timedelta(minutes=10),
        )

        self.client.login(username="maria", password="123456")
        response = self.client.post(reverse("heading"), {"action": "cancel_trip"})
        self.assertEqual(response.status_code, 302)
        aviso.refresh_from_db()
        self.assertTrue(aviso.cancelado)
        response = self.client.get(reverse("heading"))
        self.assertNotContains(response, "Viaje inicializado")

    def test_aviso_cancelado_no_se_agrega_a_la_fila(self):
        parqueadero = Parqueadero.objects.create(nombre="Visitantes", capacidad=40)
        entrada = Entrada.objects.create(nombre="Principal (Visitantes)", parqueadero=parqueadero, fila=2)
        perfil = PerfilUsuario.objects.get(user=self.user)
        aviso = AvisoEnCamino.objects.create(
            usuario=perfil,
            parqueadero=parqueadero,
            entrada=entrada,
            eta_minutos=10,
            llegada_estimada=timezone.now() - timedelta(minutes=1),
            cancelado=True,
        )

        self.client.login(username="maria", password="123456")
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        entrada.refresh_from_db()
        aviso.refresh_from_db()
        self.assertEqual(entrada.fila, 2)
        self.assertFalse(aviso.agregado_a_fila)

    def test_aviso_vencido_se_agrega_a_la_fila(self):
        parqueadero = Parqueadero.objects.create(nombre="Visitantes", capacidad=40)
        entrada = Entrada.objects.create(nombre="Principal (Visitantes)", parqueadero=parqueadero, fila=2)
        perfil = PerfilUsuario.objects.get(user=self.user)
        AvisoEnCamino.objects.create(
            usuario=perfil,
            parqueadero=parqueadero,
            entrada=entrada,
            eta_minutos=10,
            llegada_estimada=timezone.now() - timedelta(minutes=1),
        )

        self.client.login(username="maria", password="123456")
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        entrada.refresh_from_db()
        aviso = AvisoEnCamino.objects.get(entrada=entrada)
        self.assertEqual(entrada.fila, 3)
        self.assertTrue(aviso.agregado_a_fila)

    def test_payments_autenticado_muestra_funciones_de_pago(self):
        self.client.login(username="maria", password="123456")
        response = self.client.get(reverse("payments"), {"amount": 5000})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Monto a recargar")
        self.assertContains(response, "data-payment-modal")
        self.assertContains(response, 'data-cancel-url="/payments/?lang=es&tab=recharge"')
        self.assertContains(response, "payment-modal-panel")
        self.assertContains(response, "Cancelar recarga")
        self.assertContains(response, "payment-card-visual")
        self.assertContains(response, "payment-card-front")
        self.assertContains(response, "payment-card-back")
        self.assertContains(response, "data-card-back-trigger")
        self.assertContains(response, "data-card-expiry")
        self.assertContains(response, "0000 0000 0000 0000")
        self.assertContains(response, "5000")
        self.assertNotContains(response, "Personal - Automovil")

    def test_payments_autenticado_oculta_tarjeta_hasta_recargar(self):
        self.client.login(username="maria", password="123456")
        response = self.client.get(reverse("payments"), {"tab": "recharge"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Monto a recargar")
        self.assertNotContains(response, "payment-card-visual")
        self.assertNotContains(response, "0000 0000 0000 0000")

    def test_payments_autenticado_tarifas_no_muestra_recarga(self):
        self.client.login(username="maria", password="123456")
        response = self.client.get(reverse("payments"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Personal - Automovil")
        self.assertContains(response, "Tarifas de parqueadero")
        self.assertContains(response, "Recargar")
        self.assertContains(response, "Historial")
        self.assertNotContains(response, "Monto a recargar")
        self.assertNotContains(response, "payment-card-visual")

    def test_payments_autenticado_historial_muestra_estado_vacio(self):
        self.client.login(username="maria", password="123456")
        response = self.client.get(reverse("payments"), {"tab": "history"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Historial")
        self.assertContains(response, "Sin registros aun")
        self.assertNotContains(response, "Monto a recargar")
        self.assertNotContains(response, "Tarifas de parqueadero")

    def test_payments_guarda_metodo_de_pago_seguro(self):
        self.client.login(username="maria", password="123456")
        response = self.client.post(
            reverse("payments"),
            {
                "action": "save_card",
                "card_number": "4111 1111 1111 1111",
                "expiry": "12/30",
                "cvv": "123",
                "card_name": "Maria Gomez",
            },
        )
        self.assertEqual(response.status_code, 302)
        metodo = MetodoPago.objects.get(usuario__user=self.user)
        self.assertEqual(metodo.marca, "Visa")
        self.assertEqual(metodo.ultimos_cuatro, "1111")
        self.assertEqual(metodo.titular, "MARIA GOMEZ")
        field_names = [field.name for field in MetodoPago._meta.get_fields()]
        self.assertNotIn("cvv", field_names)
        self.assertNotIn("card_number", field_names)

        response = self.client.get(reverse("payments"), {"amount": 5000})
        self.assertContains(response, "payment-card-visual has-saved-card")
        self.assertContains(response, "**** **** **** 1111")
        self.assertContains(response, "12/30")
        self.assertContains(response, "MARIA GOMEZ")

    def test_payments_rechaza_tarjeta_invalida(self):
        self.client.login(username="maria", password="123456")
        response = self.client.post(
            reverse("payments"),
            {
                "action": "save_card",
                "card_number": "123",
                "expiry": "01/20",
                "cvv": "12",
                "card_name": "Maria Gomez",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(MetodoPago.objects.exists())

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

    def test_home_profesor_ve_parqueadero_de_profesores(self):
        PerfilUsuario.objects.filter(user=self.user).update(tipo_usuario="profesor")
        self.client.login(username="maria", password="123456")
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Profesores")
        self.assertContains(response, "Regional")
        self.assertContains(response, "Las Vegas")
        self.assertNotContains(response, "Regional (Profesores)")
        self.assertNotContains(response, "Las Vegas (Profesores)")

    def test_heading_profesor_ve_parqueadero_de_profesores(self):
        PerfilUsuario.objects.filter(user=self.user).update(tipo_usuario="profesor")
        self.client.login(username="maria", password="123456")
        response = self.client.get(reverse("heading"))
        self.assertContains(response, "Profesores")

    def test_home_estudiante_no_ve_parqueadero_de_profesores(self):
        self.client.login(username="maria", password="123456")
        response = self.client.get(reverse("home"))
        self.assertNotContains(response, "Profesores")

    def test_home_trabajador_no_ve_parqueadero_de_profesores(self):
        PerfilUsuario.objects.filter(user=self.user).update(tipo_usuario="trabajador")
        self.client.login(username="maria", password="123456")
        response = self.client.get(reverse("home"))
        self.assertNotContains(response, "Profesores")

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


@override_settings(FLOWGATE_WEATHER_API_ENABLED=False)
class AdminPanelTests(TestCase):
    def setUp(self):
        self.parqueadero = Parqueadero.objects.create(nombre="Norte", capacidad=100, ocupancia=30)
        self.entrada = Entrada.objects.create(nombre="Principal", parqueadero=self.parqueadero, fila=3)
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

    def test_admin_panel_muestra_campos_para_modificar_filas(self):
        self.client.login(username="staff", password="123456")
        response = self.client.get(reverse("admin_panel"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Fila Principal")
        self.assertContains(response, f'name="fila_{self.entrada.id}"')

    def test_admin_panel_muestra_avisos_en_camino(self):
        perfil = PerfilUsuario.objects.create(user=self.staff)
        AvisoEnCamino.objects.create(
            usuario=perfil,
            parqueadero=self.parqueadero,
            entrada=self.entrada,
            eta_minutos=15,
            llegada_estimada=timezone.now() + timedelta(minutes=15),
        )
        self.client.login(username="staff", password="123456")
        response = self.client.get(reverse("admin_panel"))
        self.assertContains(response, "Avisos en camino")
        self.assertContains(response, "staff")
        self.assertContains(response, "Pendiente")

    def test_admin_ve_parqueadero_de_profesores(self):
        self.client.login(username="staff", password="123456")
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Profesores")

    def test_admin_actualiza_filas_en_base_de_datos(self):
        self.client.login(username="staff", password="123456")
        response = self.client.post(
            reverse("admin_panel"),
            {
                "action": "update_availability",
                f"capacidad_{self.parqueadero.id}": "100",
                f"ocupancia_{self.parqueadero.id}": "30",
                f"fila_{self.entrada.id}": "14",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.entrada.refresh_from_db()
        self.assertEqual(self.entrada.fila, 14)

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
