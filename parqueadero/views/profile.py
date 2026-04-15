from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from parqueadero.models import PerfilUsuario, Vehiculo
from parqueadero.services import TRANSLATIONS, get_lang


@login_required(login_url="login_view")
def profile(request):
    lang = get_lang(request)
    user = request.user

    perfil, _ = PerfilUsuario.objects.get_or_create(user=user)

    try:
        vehiculo = Vehiculo.objects.get(usuario=perfil)
    except Vehiculo.DoesNotExist:
        vehiculo = None

    return render(
        request,
        "parqueadero/profile.html",
        {
            "perfil": perfil,
            "vehiculo": vehiculo,
            "lang": lang,
            "translations": TRANSLATIONS[lang],
        },
    )

