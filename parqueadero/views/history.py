from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from parqueadero.models import Historial, PerfilUsuario
from parqueadero.services import (
    TRANSLATIONS,
    get_lang,
    translate_entrance_name,
    translate_parking_name,
)


def _format_currency(value):
    return f"{value:,}".replace(",", ".")


@login_required(login_url="login_view")
def history(request):
    lang = get_lang(request)

    try:
        perfil = PerfilUsuario.objects.get(user=request.user)
        historial = list(Historial.objects.filter(usuario=perfil))
    except PerfilUsuario.DoesNotExist:
        historial = []

    for registro in historial:
        registro.display_parqueadero = translate_parking_name(registro.parqueadero.nombre, lang)
        entrada_nombre = registro.entrada.nombre.split("(", 1)[0].strip() if registro.entrada else ""
        registro.display_entrada = (
            translate_entrance_name(entrada_nombre, lang) if registro.entrada else "N/A"
        )
        registro.display_costo = _format_currency(registro.costo)

    return render(
        request,
        "parqueadero/history.html",
        {
            "historial": historial,
            "lang": lang,
            "translations": TRANSLATIONS[lang],
        },
    )

