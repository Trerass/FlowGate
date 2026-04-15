from django.contrib.auth.models import User
from django.test import TestCase

from parqueadero.models import PerfilUsuario, Vehiculo


class VehiculoModelTests(TestCase):
    def test_precio_diario_para_carro(self):
        user = User.objects.create_user(username="ana", password="123")
        perfil = PerfilUsuario.objects.create(user=user)
        vehiculo = Vehiculo.objects.create(
            usuario=perfil,
            placa="ABC123",
            marca="Mazda",
            modelo="3",
            color="Rojo",
            tipo_vehiculo="carro",
            es_electrico=False,
        )
        self.assertEqual(vehiculo.precio_diario, 8700)

    def test_precio_diario_es_cero_para_electrico(self):
        user = User.objects.create_user(username="luis", password="123")
        perfil = PerfilUsuario.objects.create(user=user)
        vehiculo = Vehiculo.objects.create(
            usuario=perfil,
            placa="ELE123",
            marca="BYD",
            modelo="Seal",
            color="Azul",
            tipo_vehiculo="carro",
            es_electrico=True,
        )
        self.assertEqual(vehiculo.precio_diario, 0)
