from parqueadero.models import RechargeTransaction
from parqueadero.services.payments import apply_transaction_status


DEMO_PAYMENT_METHODS = {
    "card": "Tarjeta",
    "pse": "PSE",
    "nequi": "Nequi",
}


def normalize_demo_method(value):
    return DEMO_PAYMENT_METHODS.get(value, DEMO_PAYMENT_METHODS["card"])


def apply_demo_payment(recharge, result, payment_method):
    if result == "declined":
        status = RechargeTransaction.STATUS_DECLINED
    elif result in {"voided", "cancelled", "canceled"}:
        status = RechargeTransaction.STATUS_VOIDED
    else:
        status = RechargeTransaction.STATUS_APPROVED

    method = normalize_demo_method(payment_method)
    return apply_transaction_status(
        recharge,
        status=status,
        provider_transaction_id=f"demo-{recharge.reference}",
        payment_method=method,
        raw_response={
            "provider": RechargeTransaction.PROVIDER_DEMO,
            "result": result,
            "payment_method": method,
        },
    )
