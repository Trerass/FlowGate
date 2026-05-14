from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch

from parqueadero.models import (
    AvisoEnCamino,
    Entrada,
    Parqueadero,
    PerfilUsuario,
    RechargeTransaction,
    Vehiculo,
    Wallet,
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
            reverse("create_recharge"),
            {"amount": "20000"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login_view"), response["Location"])
        self.assertFalse(RechargeTransaction.objects.exists())

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
        self.assertContains(response, "Personas en camino")
        self.assertContains(response, "1 en camino")

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

    def test_heading_muestra_personas_en_camino_por_entrada(self):
        parqueadero = Parqueadero.objects.create(nombre="Visitantes", capacidad=40)
        entrada = Entrada.objects.create(nombre="Principal (Visitantes)", parqueadero=parqueadero, fila=2)
        otra_entrada = Entrada.objects.create(nombre="Norte (Visitantes)", parqueadero=parqueadero, fila=0)
        otro_usuario = User.objects.create_user(username="carlos", password="123456")
        otro_perfil = PerfilUsuario.objects.create(user=otro_usuario)
        perfil = PerfilUsuario.objects.get(user=self.user)
        AvisoEnCamino.objects.create(
            usuario=perfil,
            parqueadero=parqueadero,
            entrada=entrada,
            eta_minutos=10,
            llegada_estimada=timezone.now() + timedelta(minutes=10),
        )
        AvisoEnCamino.objects.create(
            usuario=otro_perfil,
            parqueadero=parqueadero,
            entrada=entrada,
            eta_minutos=12,
            llegada_estimada=timezone.now() + timedelta(minutes=12),
        )
        AvisoEnCamino.objects.create(
            usuario=otro_perfil,
            parqueadero=parqueadero,
            entrada=otra_entrada,
            eta_minutos=5,
            llegada_estimada=timezone.now() + timedelta(minutes=5),
            cancelado=True,
        )

        self.client.login(username="maria", password="123456")
        response = self.client.get(reverse("heading"))

        self.assertContains(response, "2 en camino")
        self.assertContains(response, "0 en camino")

    def test_heading_status_retorna_conteos_en_tiempo_real(self):
        parqueadero = Parqueadero.objects.create(nombre="Visitantes", capacidad=40)
        entrada = Entrada.objects.create(nombre="Principal (Visitantes)", parqueadero=parqueadero, fila=2)
        otro_usuario = User.objects.create_user(username="carlos", password="123456")
        otro_perfil = PerfilUsuario.objects.create(user=otro_usuario)
        perfil = PerfilUsuario.objects.get(user=self.user)
        AvisoEnCamino.objects.create(
            usuario=perfil,
            parqueadero=parqueadero,
            entrada=entrada,
            eta_minutos=10,
            llegada_estimada=timezone.now() + timedelta(minutes=10),
        )
        AvisoEnCamino.objects.create(
            usuario=otro_perfil,
            parqueadero=parqueadero,
            entrada=entrada,
            eta_minutos=20,
            llegada_estimada=timezone.now() + timedelta(minutes=20),
        )

        self.client.login(username="maria", password="123456")
        response = self.client.get(reverse("heading_status"))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["entries"][str(entrada.id)]["queue"], 2)
        self.assertEqual(data["entries"][str(entrada.id)]["on_the_way"], 2)
        self.assertEqual(data["active_trip"]["entry_id"], entrada.id)
        self.assertEqual(data["active_trip"]["on_the_way"], 2)

    def test_payments_autenticado_muestra_funciones_de_recarga(self):
        self.client.login(username="maria", password="123456")
        response = self.client.get(reverse("payments"), {"tab": "recharge"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Monto a recargar")
        self.assertContains(response, "Recarga segura")
        self.assertNotContains(response, "Modo demo académico")
        self.assertNotContains(response, "Esta transacción no mueve dinero real.")
        self.assertContains(response, reverse("create_recharge"))
        self.assertContains(response, 'data-cop-input')
        self.assertContains(response, 'data-count="0"')
        self.assertNotContains(response, "Personal - Automovil")
        self.assertNotContains(response, "Numero de tarjeta")

    def test_payments_autenticado_oculta_modal_hasta_crear_recarga(self):
        self.client.login(username="maria", password="123456")
        response = self.client.get(reverse("payments"), {"tab": "recharge"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Monto a recargar")
        self.assertNotContains(response, "wompi-confirm-modal")
        self.assertFalse(RechargeTransaction.objects.exists())

    def test_selector_idioma_preserva_query_actual(self):
        self.client.login(username="maria", password="123456")
        response = self.client.get(
            reverse("payments"),
            {"tab": "recharge", "amount": "5000", "lang": "es"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "/payments/?tab=recharge&amp;amount=5000&amp;lang=en")
        self.assertContains(response, "/payments/?tab=recharge&amp;amount=5000&amp;lang=es")

    def test_payments_autenticado_tarifas_no_muestra_recarga(self):
        self.client.login(username="maria", password="123456")
        response = self.client.get(reverse("payments"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Personal - Automovil")
        self.assertContains(response, "Tarifas de parqueadero")
        self.assertContains(response, "Recargar")
        self.assertContains(response, "Historial")
        self.assertNotContains(response, "Monto a recargar")
        self.assertNotContains(response, "wompi-confirm-modal")

    def test_payments_autenticado_historial_muestra_estado_vacio(self):
        self.client.login(username="maria", password="123456")
        response = self.client.get(reverse("payments"), {"tab": "history"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Historial")
        self.assertContains(response, "Sin registros aun")
        self.assertContains(response, "No tienes recargas registradas todavia.")
        self.assertNotContains(response, "Monto a recargar")
        self.assertNotContains(response, "Tarifas de parqueadero")

    @override_settings(
        WOMPI_PUBLIC_KEY="pub_test",
        WOMPI_PRIVATE_KEY="prv_test",
        WOMPI_INTEGRITY_SECRET="integrity_test",
        PAYMENT_PROVIDER="wompi",
        APP_BASE_URL="http://testserver",
    )
    def test_create_recharge_crea_transaccion_pendiente_con_wompi_real(self):
        self.client.login(username="maria", password="123456")
        response = self.client.post(
            reverse("create_recharge"),
            {"amount": "$ 20.000 COP"},
        )
        self.assertEqual(response.status_code, 302)
        recharge = RechargeTransaction.objects.get(user=self.user)
        self.assertEqual(recharge.amount_cop, 20000)
        self.assertEqual(recharge.amount_in_cents, 2000000)
        self.assertEqual(recharge.provider, RechargeTransaction.PROVIDER_WOMPI)
        self.assertEqual(recharge.status, RechargeTransaction.STATUS_PENDING)
        self.assertFalse(recharge.credited)
        self.assertIn("reference=", response["Location"])
        self.assertEqual(Wallet.objects.get(user=self.user).balance_cop, 0)

        response = self.client.get(response["Location"])
        self.assertContains(response, "data-payment-modal")
        self.assertContains(response, "Continuar al pago")
        self.assertContains(response, "checkout.wompi.co")
        self.assertContains(response, recharge.reference)
        self.assertContains(response, "Procesado por Wompi")

    def test_create_recharge_rechaza_monto_invalido(self):
        self.client.login(username="maria", password="123456")
        response = self.client.post(
            reverse("create_recharge"),
            {"amount": "0"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(RechargeTransaction.objects.exists())

    @override_settings(PAYMENT_PROVIDER="wompi", WOMPI_PUBLIC_KEY="", WOMPI_INTEGRITY_SECRET="")
    def test_create_recharge_sin_configuracion_no_crea_transaccion(self):
        self.client.login(username="maria", password="123456")
        response = self.client.post(
            reverse("create_recharge"),
            {"amount": "20000"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(RechargeTransaction.objects.exists())

    @override_settings(PAYMENT_PROVIDER="demo", WOMPI_PUBLIC_KEY="", WOMPI_INTEGRITY_SECRET="")
    def test_demo_checkout_permite_probar_recarga_local(self):
        self.client.login(username="maria", password="123456")
        response = self.client.post(reverse("create_recharge"), {"amount": "20000"})
        self.assertEqual(response.status_code, 302)
        recharge = RechargeTransaction.objects.get(user=self.user)

        response = self.client.get(response["Location"])
        self.assertContains(response, "Pago seguro")
        self.assertContains(response, "Revisa el monto antes de continuar con el pago seguro.")
        self.assertNotContains(response, "Modo demo académico")
        self.assertNotContains(response, "Esta transacción no mueve dinero real.")
        self.assertContains(response, "payment-card-visual")
        self.assertContains(response, "Numero de tarjeta")
        self.assertContains(response, "0000 0000 0000 0000")
        self.assertContains(response, "data-demo-card-panel")
        self.assertContains(response, "data-card-cvv")
        self.assertContains(response, "Realizar pago")
        self.assertNotContains(response, "Billetera digital")
        self.assertNotContains(response, "Guardar tarjeta y efectuar pago")

        response = self.client.post(
            reverse("demo_payment"),
            {"reference": recharge.reference, "result": "approved", "payment_method": "nequi"},
        )
        self.assertEqual(response.status_code, 302)
        recharge.refresh_from_db()
        self.assertEqual(recharge.status, RechargeTransaction.STATUS_APPROVED)
        self.assertEqual(recharge.payment_method, "Nequi")
        self.assertEqual(Wallet.objects.get(user=self.user).balance_cop, 20000)

    @override_settings(PAYMENT_PROVIDER="demo", WOMPI_PUBLIC_KEY="", WOMPI_INTEGRITY_SECRET="")
    def test_demo_checkout_rechazado_no_actualiza_saldo(self):
        self.client.login(username="maria", password="123456")
        Wallet.objects.create(user=self.user, balance_cop=5000)
        response = self.client.post(reverse("create_recharge"), {"amount": "20000"})
        recharge = RechargeTransaction.objects.get(user=self.user)

        response = self.client.post(
            reverse("demo_payment"),
            {"reference": recharge.reference, "result": "declined", "payment_method": "pse"},
        )
        self.assertEqual(response.status_code, 302)
        recharge.refresh_from_db()
        self.assertEqual(recharge.status, RechargeTransaction.STATUS_DECLINED)
        self.assertEqual(recharge.payment_method, "PSE")
        self.assertEqual(Wallet.objects.get(user=self.user).balance_cop, 5000)

    @override_settings(PAYMENT_PROVIDER="demo", WOMPI_PUBLIC_KEY="", WOMPI_INTEGRITY_SECRET="")
    def test_demo_checkout_cancelado_no_actualiza_saldo(self):
        self.client.login(username="maria", password="123456")
        Wallet.objects.create(user=self.user, balance_cop=5000)
        response = self.client.post(reverse("create_recharge"), {"amount": "20000"})
        recharge = RechargeTransaction.objects.get(user=self.user)

        response = self.client.post(
            reverse("demo_payment"),
            {"reference": recharge.reference, "result": "voided", "payment_method": "nequi"},
        )
        self.assertEqual(response.status_code, 302)
        recharge.refresh_from_db()
        self.assertEqual(recharge.status, RechargeTransaction.STATUS_VOIDED)
        self.assertEqual(Wallet.objects.get(user=self.user).balance_cop, 5000)

    @override_settings(PAYMENT_PROVIDER="wompi", WOMPI_PUBLIC_KEY="", WOMPI_INTEGRITY_SECRET="")
    def test_demo_checkout_no_funciona_si_el_proveedor_es_wompi(self):
        self.client.login(username="maria", password="123456")
        recharge = RechargeTransaction.objects.create(
            user=self.user,
            amount_cop=20000,
            amount_in_cents=2000000,
            provider=RechargeTransaction.PROVIDER_DEMO,
            reference="FG-DEMO-DISABLED",
        )
        response = self.client.post(
            reverse("demo_payment"),
            {"reference": recharge.reference, "result": "approved"},
        )
        self.assertEqual(response.status_code, 400)

    @override_settings(WOMPI_PRIVATE_KEY="prv_test")
    def test_wompi_return_aprobado_actualiza_saldo(self):
        self.client.login(username="maria", password="123456")
        Wallet.objects.create(user=self.user, balance_cop=5000)
        recharge = RechargeTransaction.objects.create(
            user=self.user,
            amount_cop=20000,
            amount_in_cents=2000000,
            reference="FG-RETURN",
        )
        wompi_data = {
            "id": "wompi-return",
            "reference": recharge.reference,
            "status": "APPROVED",
            "amount_in_cents": recharge.amount_in_cents,
            "currency": recharge.currency,
        }

        with patch("parqueadero.views.payments.get_wompi_transaction", return_value=wompi_data):
            response = self.client.get(reverse("wompi_return"), {"id": "wompi-return"})

        self.assertEqual(response.status_code, 302)
        self.assertIn("tab=history", response["Location"])
        recharge.refresh_from_db()
        self.assertEqual(recharge.status, RechargeTransaction.STATUS_APPROVED)
        self.assertEqual(Wallet.objects.get(user=self.user).balance_cop, 25000)

    @override_settings(WOMPI_PRIVATE_KEY="prv_test")
    def test_wompi_return_rechazado_no_actualiza_saldo(self):
        self.client.login(username="maria", password="123456")
        Wallet.objects.create(user=self.user, balance_cop=5000)
        recharge = RechargeTransaction.objects.create(
            user=self.user,
            amount_cop=20000,
            amount_in_cents=2000000,
            reference="FG-DECLINED-RETURN",
        )
        wompi_data = {
            "id": "wompi-return",
            "reference": recharge.reference,
            "status": "DECLINED",
            "amount_in_cents": recharge.amount_in_cents,
            "currency": recharge.currency,
        }

        with patch("parqueadero.views.payments.get_wompi_transaction", return_value=wompi_data):
            response = self.client.get(reverse("wompi_return"), {"id": "wompi-return"})

        self.assertEqual(response.status_code, 302)
        recharge.refresh_from_db()
        self.assertEqual(recharge.status, RechargeTransaction.STATUS_DECLINED)
        self.assertEqual(Wallet.objects.get(user=self.user).balance_cop, 5000)

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
