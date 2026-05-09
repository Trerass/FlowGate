from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render

from parqueadero.models import AvisoEnCamino, Entrada, Parqueadero
from parqueadero.services import TRANSLATIONS, get_lang, process_due_arrivals


def _is_staff_user(user):
    return user.is_authenticated and user.is_staff


@login_required(login_url="login_view")
@user_passes_test(_is_staff_user, login_url="home")
def admin_panel(request):
    lang = get_lang(request)
    process_due_arrivals()

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "update_availability":
            for parqueadero in Parqueadero.objects.all():
                ocupancia = request.POST.get(f"ocupancia_{parqueadero.id}", parqueadero.ocupancia)
                capacidad = request.POST.get(f"capacidad_{parqueadero.id}", parqueadero.capacidad)

                if str(ocupancia).isdigit() and str(capacidad).isdigit():
                    parqueadero.capacidad = max(0, int(capacidad))
                    parqueadero.ocupancia = min(parqueadero.capacidad, max(0, int(ocupancia)))
                    parqueadero.save()

            for entrada in Entrada.objects.all():
                fila = request.POST.get(f"fila_{entrada.id}", entrada.fila)
                if str(fila).isdigit():
                    entrada.fila = max(0, int(fila))
                    entrada.save()

            messages.success(request, "Disponibilidad actualizada correctamente.")
            return redirect(f"{request.path}?lang={lang}")

    parqueaderos = []
    for parqueadero in Parqueadero.objects.prefetch_related("entrada_set").all().order_by("nombre"):
        disponibles = max(parqueadero.capacidad - parqueadero.ocupancia, 0)
        porcentaje = round((parqueadero.ocupancia / parqueadero.capacidad) * 100) if parqueadero.capacidad else 0
        parqueaderos.append(
            {
                "id": parqueadero.id,
                "nombre": parqueadero.nombre,
                "capacidad": parqueadero.capacidad,
                "ocupancia": parqueadero.ocupancia,
                "disponibles": disponibles,
                "porcentaje": porcentaje,
                "entradas": parqueadero.entrada_set.all().order_by("nombre"),
            }
        )

    return render(
        request,
        "parqueadero/admin_panel.html",
        {
            "lang": lang,
            "translations": TRANSLATIONS[lang],
            "parqueaderos": parqueaderos,
            "avisos_en_camino": AvisoEnCamino.objects.select_related(
                "usuario__user",
                "parqueadero",
                "entrada",
            )[:8],
        },
    )
