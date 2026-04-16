from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from parqueadero.models import Historial, PerfilUsuario
from parqueadero.services import TRANSLATIONS, get_lang


@login_required(login_url="login_view")
def history(request):
    lang = get_lang(request)

    try:
        perfil = PerfilUsuario.objects.get(user=request.user)
        historial = Historial.objects.filter(usuario=perfil)
    except PerfilUsuario.DoesNotExist:
        historial = []

    return render(
        request,
        "parqueadero/history.html",
        {
            "historial": historial,
            "lang": lang,
            "translations": TRANSLATIONS[lang],
        },
    )

