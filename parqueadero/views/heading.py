from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from parqueadero.models import AvisoEnCamino, Entrada, PerfilUsuario
from parqueadero.services import TRANSLATIONS, get_lang, get_parking_data
from parqueadero.services.parking_service import _can_view_parking


def _clean_entry_name(name):
    return name.split("(", 1)[0].strip()


@login_required(login_url="login_view")
def heading(request):
    lang = get_lang(request)
    dashboard_data = get_parking_data(lang, request.user)
    perfil, _ = PerfilUsuario.objects.get_or_create(user=request.user)
    try:
        eta = int(request.POST.get("eta", request.GET.get("eta", 15)))
    except (TypeError, ValueError):
        eta = 15
    selected_parking = request.POST.get("parking") or request.GET.get("parking")
    selected_entry = request.POST.get("entrada") or request.GET.get("entrada")

    if request.method == "POST":
        if request.POST.get("action") == "cancel_trip":
            AvisoEnCamino.objects.filter(
                usuario=perfil,
                agregado_a_fila=False,
                cancelado=False,
            ).update(cancelado=True)
            messages.success(request, "Viaje cancelado correctamente.")
            return redirect(f"{request.path}?lang={lang}")

        try:
            entrada = Entrada.objects.select_related("parqueadero").get(id=selected_entry)
        except (Entrada.DoesNotExist, ValueError, TypeError):
            messages.error(request, "Selecciona una entrada valida para avisar que vas en camino.")
        else:
            parking_matches_entry = str(entrada.parqueadero_id) == str(selected_parking)
            if not parking_matches_entry or not _can_view_parking(entrada.parqueadero, request.user):
                messages.error(request, "Selecciona un parqueadero y una entrada disponibles para tu usuario.")
            else:
                eta = max(0, min(120, eta))
                AvisoEnCamino.objects.filter(
                    usuario=perfil,
                    agregado_a_fila=False,
                    cancelado=False,
                ).update(cancelado=True)
                AvisoEnCamino.objects.create(
                    usuario=perfil,
                    parqueadero=entrada.parqueadero,
                    entrada=entrada,
                    eta_minutos=eta,
                    llegada_estimada=timezone.now() + timedelta(minutes=eta),
                )
                return redirect(f"{request.path}?lang={lang}")

    parking_options = []
    for parqueadero in dashboard_data["parqueaderos"]:
        adjusted_available = max(0, parqueadero["available_slots"] - max(0, eta - 10) // 3)
        parking_options.append(
            {
                **parqueadero,
                "projected_available": adjusted_available,
                "selected": str(selected_parking) == str(parqueadero["id"]) or (not selected_parking and not parking_options),
            }
        )

    active_notice = AvisoEnCamino.objects.select_related(
        "parqueadero",
        "entrada",
    ).filter(
        usuario=perfil,
        agregado_a_fila=False,
        cancelado=False,
    ).first()
    active_trip = None
    if active_notice:
        remaining_seconds = max(0, int((active_notice.llegada_estimada - timezone.now()).total_seconds()))
        remaining_minutes = (remaining_seconds + 59) // 60
        occupancy_percent = (
            round((active_notice.parqueadero.ocupancia / active_notice.parqueadero.capacidad) * 100)
            if active_notice.parqueadero.capacidad
            else 0
        )
        active_trip = {
            "parqueadero": active_notice.parqueadero,
            "entrada": active_notice.entrada,
            "entrada_nombre": _clean_entry_name(active_notice.entrada.nombre),
            "eta_minutos": active_notice.eta_minutos,
            "remaining_minutes": remaining_minutes,
            "available_slots": max(active_notice.parqueadero.capacidad - active_notice.parqueadero.ocupancia, 0),
            "occupancy_percent": occupancy_percent,
            "queue": max(0, active_notice.entrada.fila),
        }

    context = {
        "lang": lang,
        "translations": TRANSLATIONS[lang],
        "user": request.user,
        "eta": eta,
        "parking_options": parking_options,
        "active_trip": active_trip,
    }
    return render(request, "parqueadero/heading.html", context)
