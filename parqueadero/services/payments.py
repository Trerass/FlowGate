import re
import uuid
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from parqueadero.models import RechargeTransaction, Wallet


MIN_RECHARGE_COP = 1000
MAX_RECHARGE_COP = 2_000_000


def get_payment_provider():
    provider = getattr(settings, "PAYMENT_PROVIDER", "demo")
    return provider if provider in {"demo", "wompi"} else "demo"


def is_demo_provider():
    return get_payment_provider() == "demo"


def is_wompi_provider():
    return get_payment_provider() == "wompi"


def normalize_amount_input(value):
    raw = str(value or "").strip()
    if not raw:
        raise ValueError("empty")
    if re.search(r"(^|\s)-\s*\d", raw):
        raise ValueError("invalid")

    normalized = re.sub(r"[^\d,.]", "", raw)
    if "," in normalized and "." in normalized:
        normalized = normalized.replace(".", "").split(",", 1)[0]
    elif "," in normalized:
        normalized = normalized.split(",", 1)[0]
    else:
        normalized = normalized.replace(".", "")

    if not normalized.isdigit():
        raise ValueError("invalid")

    try:
        amount = int(Decimal(normalized))
    except (InvalidOperation, ValueError):
        raise ValueError("invalid")

    if amount < MIN_RECHARGE_COP:
        raise ValueError("too_low")
    if amount > MAX_RECHARGE_COP:
        raise ValueError("too_high")
    return amount


def amount_to_cents(amount_cop):
    return int(amount_cop) * 100


def generate_reference(user_id=None):
    user_part = f"U{user_id}" if user_id else "S"
    timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
    suffix = uuid.uuid4().hex[:10].upper()
    return f"FG-{timestamp}-{user_part}-{suffix}"


def create_recharge_transaction(user, amount_cop, provider, session_key="", payment_method=""):
    return RechargeTransaction.objects.create(
        user=user if getattr(user, "is_authenticated", False) else None,
        session_key=session_key or "",
        amount_cop=amount_cop,
        amount_in_cents=amount_to_cents(amount_cop),
        currency="COP",
        provider=provider,
        payment_method=payment_method,
        reference=generate_reference(getattr(user, "id", None)),
        status=RechargeTransaction.STATUS_PENDING,
    )


def apply_transaction_status(
    local_recharge,
    status,
    provider_transaction_id="",
    payment_method="",
    raw_response=None,
):
    with transaction.atomic():
        recharge = RechargeTransaction.objects.select_for_update().get(pk=local_recharge.pk)
        recharge.status = status
        recharge.raw_response = raw_response or {}
        if provider_transaction_id:
            recharge.provider_transaction_id = provider_transaction_id
            if recharge.provider == RechargeTransaction.PROVIDER_WOMPI:
                recharge.wompi_transaction_id = provider_transaction_id
        if payment_method:
            recharge.payment_method = payment_method

        if (
            status == RechargeTransaction.STATUS_APPROVED
            and not recharge.credited
            and not recharge.is_credited
            and recharge.user_id
        ):
            Wallet.objects.select_for_update().get_or_create(user=recharge.user)
            Wallet.objects.filter(user=recharge.user).update(
                balance_cop=F("balance_cop") + recharge.amount_cop
            )
            recharge.credited = True
            recharge.is_credited = True

        recharge.save(update_fields=[
            "status",
            "provider_transaction_id",
            "wompi_transaction_id",
            "payment_method",
            "raw_response",
            "credited",
            "is_credited",
            "updated_at",
        ])

    recharge.refresh_from_db()
    return recharge
