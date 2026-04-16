from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import redirect, render

from parqueadero.models import Historial, PerfilUsuario, Vehiculo
from parqueadero.services import TRANSLATIONS, get_lang


def _update_profile(user, perfil, request):
    full_name = request.POST.get("full_name", "").strip()
    email = request.POST.get("email", "").strip()
    telefono = request.POST.get("telefono", "").strip()
    codigo = request.POST.get("codigo_estudiantil", "").strip()
    tipo_usuario = request.POST.get("tipo_usuario", "estudiante")

    name_parts = full_name.split(" ", 1)
    user.first_name = name_parts[0] if name_parts else ""
    user.last_name = name_parts[1] if len(name_parts) > 1 else ""
    user.email = email
    user.save()

    perfil.telefono = telefono
    perfil.codigo_estudiantil = codigo
    perfil.tipo_usuario = tipo_usuario
    perfil.save()


def _update_vehicle(perfil, request):
    vehiculo, _ = Vehiculo.objects.get_or_create(
        usuario=perfil,
        defaults={
            "placa": request.POST.get("placa", "").strip() or f"{perfil.user.id}TEMP",
            "marca": "",
            "modelo": "",
            "color": "",
            "tipo_vehiculo": "carro",
        },
    )
    vehiculo.placa = request.POST.get("placa", "").strip()
    vehiculo.marca = request.POST.get("marca", "").strip()
    vehiculo.modelo = request.POST.get("modelo", "").strip()
    vehiculo.color = request.POST.get("color", "").strip()
    vehiculo.tipo_vehiculo = request.POST.get("tipo_vehiculo", "carro")
    vehiculo.es_electrico = request.POST.get("es_electrico") == "on"
    vehiculo.save()


@login_required(login_url="login_view")
def profile(request):
    lang = get_lang(request)
    user = request.user
    perfil, _ = PerfilUsuario.objects.get_or_create(user=user)
    vehiculo = Vehiculo.objects.filter(usuario=perfil).first()
    active_tab = request.GET.get("tab", "info")

    if request.method == "POST":
        action = request.POST.get("action")

        try:
            if action == "update_profile":
                _update_profile(user, perfil, request)
                messages.success(request, TRANSLATIONS[lang]["profile_updated"])
            elif action == "update_vehicle":
                _update_vehicle(perfil, request)
                messages.success(request, TRANSLATIONS[lang]["vehicle_updated"])
            elif action == "delete_vehicle":
                if vehiculo:
                    vehiculo.delete()
                    messages.success(request, TRANSLATIONS[lang]["vehicle_deleted"])
            elif action == "delete_account":
                user.delete()
                logout(request)
                messages.success(request, TRANSLATIONS[lang]["account_deleted"])
                return redirect("home")
        except Exception:
            messages.error(request, TRANSLATIONS[lang]["errors_found"])

        return redirect(f"{request.path}?lang={lang}&tab={active_tab}")

    historial = Historial.objects.filter(usuario=perfil)[:8]
    full_name = f"{user.first_name} {user.last_name}".strip() or user.username

    return render(
        request,
        "parqueadero/profile.html",
        {
            "perfil": perfil,
            "vehiculo": vehiculo,
            "historial": historial,
            "full_name": full_name,
            "active_tab": active_tab,
            "lang": lang,
            "translations": TRANSLATIONS[lang],
        },
    )
