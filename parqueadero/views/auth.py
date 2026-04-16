from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect, render

from parqueadero.models import PerfilUsuario
from parqueadero.services import TRANSLATIONS, get_lang


def login_view(request):
    lang = get_lang(request)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "login":
            username = request.POST.get("username")
            password = request.POST.get("password")
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect("home")

        elif action == "signup":
            username = request.POST.get("signup_username")
            email = request.POST.get("email")
            password = request.POST.get("signup_password")
            phone = request.POST.get("phone")
            codigo = request.POST.get("codigo")
            tipo_usuario = request.POST.get("tipo_usuario", "estudiante")

            if User.objects.filter(username=username).exists():
                return render(
                    request,
                    "parqueadero/login.html",
                    {
                        "error": "El usuario ya existe",
                        "lang": lang,
                        "translations": TRANSLATIONS[lang],
                    },
                )

            user = User.objects.create_user(username=username, email=email, password=password)
            PerfilUsuario.objects.create(
                user=user,
                telefono=phone,
                codigo_estudiantil=codigo,
                tipo_usuario=tipo_usuario,
            )

            login(request, user)
            return redirect("profile")

    return render(
        request,
        "parqueadero/login.html",
        {
            "lang": lang,
            "translations": TRANSLATIONS[lang],
        },
    )


def logout_view(request):
    logout(request)
    return redirect("home")

