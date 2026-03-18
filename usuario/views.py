from django.shortcuts import render,redirect
from django.contrib import messages
from .models import Usuario,Rol
from django.contrib.auth.hashers import check_password, make_password


def login_view(request):

    if request.method == "POST":

        correo = request.POST.get("correo")
        password = request.POST.get("password")

        try:
            usuario = Usuario.objects.get(correo=correo)

            if check_password(password, usuario.password):

                print("ROL DEL USUARIO:", usuario.rol_id)

                request.session["usuario_id"] = usuario.id
                request.session["usuario_nombre"] = usuario.nombres
                request.session["usuario_rol"] = usuario.rol.nombre_rol


                if usuario.rol.nombre_rol == "Administrador":
                    return redirect("inicio_admin")

                elif usuario.rol.nombre_rol == "Cliente":
                    return redirect("inicio_cliente")

                elif usuario.rol.nombre_rol == "Vendedor":
                    return redirect("inicio_vendedor")

                else:
                    return render(request, "login.html", {"error": "Rol no válido"})

            else:
                return render(request, "login.html", {"error": "Contraseña incorrecta"})

        except Usuario.DoesNotExist:
            return render(request, "login.html", {"error": "Usuario no existe"})

    return render(request, "login.html")

def inicio_admin(request):

    if "usuario_id" not in request.session:
        return redirect("login")

    if request.session.get("usuario_rol") != "Administrador":
        return redirect("login")

    nombre = request.session.get("usuario_nombre")

    return render(request, "admin.html", {"nombre": nombre})

def landing(request):
    return render(request, "inicio_cliente.html")

def inicio_cliente(request):

    if "usuario_id" not in request.session:
        return redirect("login")

    if request.session.get("usuario_rol") != "Cliente":
        return redirect("login")

    nombre = request.session.get("usuario_nombre")

    return render(request, "inicio_cliente.html", {"nombre": nombre})


def inicio_vendedor(request):

    if "usuario_id" not in request.session:
        return redirect("login")

    if request.session.get("usuario_rol") != "Vendedor":
        return redirect("login")

    nombre = request.session.get("usuario_nombre")

    return render(request, "inicio.html", {"nombre": nombre})




def logout_view(request):
    request.session.flush()
    return redirect("landing")

def registro_view(request):

    if request.method == "POST":

        nombres = request.POST["nombres"]
        apellidos = request.POST["apellidos"]
        correo = request.POST["correo"]
        fecha_nacimiento = request.POST["fecha_nacimiento"]
        tipo_identificacion = request.POST["tipo_identificacion"]
        num_identificacion = request.POST["num_identificacion"]
        password = request.POST["password"]

        if Usuario.objects.filter(num_identificacion=num_identificacion).exists():
            messages.error(request, "El número de identificación ya está registrado.")
            return render(request, "registro.html")

        if Usuario.objects.filter(correo=correo).exists():
            messages.error(request, "El correo ya se encuentra registrado.")
            return render(request, "registro.html")

        rol = Rol.objects.get(id=2)

        usuario = Usuario(
            rol=rol,
            nombres=nombres,
            apellidos=apellidos,
            correo=correo,
            fecha_nacimiento=fecha_nacimiento,
            tipo_identificacion=tipo_identificacion,
            num_identificacion=num_identificacion,
            password=make_password(password)
        )

        usuario.save()

        messages.success(request, "Usuario registrado correctamente.")

        return redirect("login")

    return render(request, "registro.html")

