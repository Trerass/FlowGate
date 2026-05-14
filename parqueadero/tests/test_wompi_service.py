import hashlib

from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from parqueadero.models import RechargeTransaction, Wallet
from parqueadero.services.wompi import (
    apply_wompi_transaction_status,
    generate_integrity_signature,
    normalize_amount_input,
)


class WompiServiceTests(TestCase):
    @override_settings(WOMPI_INTEGRITY_SECRET="secret_integrity")
    def test_generate_integrity_signature(self):
        signature = generate_integrity_signature("FG-TEST", 2000000, "COP")
        expected = hashlib.sha256("FG-TEST2000000COPsecret_integrity".encode("utf-8")).hexdigest()
        self.assertEqual(signature, expected)

    def test_normalize_amount_input(self):
        self.assertEqual(normalize_amount_input("$ 20.000 COP"), 20000)
        self.assertEqual(normalize_amount_input("15000"), 15000)

        with self.assertRaises(ValueError):
            normalize_amount_input("0")
        with self.assertRaises(ValueError):
            normalize_amount_input("-5000")

    def test_apply_approved_transaction_credits_wallet_once(self):
        user = User.objects.create_user(username="ana", password="123456")
        Wallet.objects.create(user=user, balance_cop=10000)
        recharge = RechargeTransaction.objects.create(
            user=user,
            amount_cop=20000,
            amount_in_cents=2000000,
            reference="FG-APPROVED",
        )
        wompi_data = {
            "id": "wompi-123",
            "reference": recharge.reference,
            "status": "APPROVED",
        }

        apply_wompi_transaction_status(recharge, wompi_data)
        apply_wompi_transaction_status(recharge, wompi_data)

        wallet = Wallet.objects.get(user=user)
        recharge.refresh_from_db()
        self.assertEqual(wallet.balance_cop, 30000)
        self.assertTrue(recharge.is_credited)
        self.assertEqual(recharge.status, RechargeTransaction.STATUS_APPROVED)

    def test_apply_declined_transaction_does_not_credit_wallet(self):
        user = User.objects.create_user(username="ana", password="123456")
        Wallet.objects.create(user=user, balance_cop=10000)
        recharge = RechargeTransaction.objects.create(
            user=user,
            amount_cop=20000,
            amount_in_cents=2000000,
            reference="FG-DECLINED",
        )

        apply_wompi_transaction_status(
            recharge,
            {"id": "wompi-456", "reference": recharge.reference, "status": "DECLINED"},
        )

        wallet = Wallet.objects.get(user=user)
        recharge.refresh_from_db()
        self.assertEqual(wallet.balance_cop, 10000)
        self.assertFalse(recharge.is_credited)
        self.assertEqual(recharge.status, RechargeTransaction.STATUS_DECLINED)

    def test_apply_approved_transaction_with_wrong_amount_is_error(self):
        user = User.objects.create_user(username="ana", password="123456")
        Wallet.objects.create(user=user, balance_cop=10000)
        recharge = RechargeTransaction.objects.create(
            user=user,
            amount_cop=20000,
            amount_in_cents=2000000,
            reference="FG-WRONG-AMOUNT",
        )

        apply_wompi_transaction_status(
            recharge,
            {
                "id": "wompi-789",
                "reference": recharge.reference,
                "status": "APPROVED",
                "amount_in_cents": 1000000,
                "currency": "COP",
            },
        )

        wallet = Wallet.objects.get(user=user)
        recharge.refresh_from_db()
        self.assertEqual(wallet.balance_cop, 10000)
        self.assertFalse(recharge.is_credited)
        self.assertEqual(recharge.status, RechargeTransaction.STATUS_ERROR)
