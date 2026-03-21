from django.shortcuts import render,redirect
from django.contrib import messages
from .models import Usuario,Rol
from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import send_mail,EmailMultiAlternatives
from django.conf import settings
import random
from django.utils.timezone import now
from datetime import timedelta


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


        if not num_identificacion.isdigit() or int(num_identificacion) <= 0:
            messages.error(request, "Número de documento no válido.")
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
        
        asunto = "Bienvenido a UniSena 🎉"

        mensaje_texto = f"Hola {nombres}, tu cuenta fue creada correctamente."

        mensaje_html = f"""
        <html>
        <body style="font-family: Arial; background-color: #f5f7fa; padding: 20px;">
            
            <div style="max-width: 500px; margin: auto; background: white; border-radius: 10px; padding: 20px; text-align: center;">
            
            <!-- LOGO -->
            <img src="https://i.imgur.com/2yaf2wb.png" width="80" style="margin-bottom: 10px;" />

            <h2 style="color: #125f58;">Bienvenido a UniSena</h2>

            <p style="color: #555;">
                Hola <strong>{nombres}</strong>, tu cuenta fue creada correctamente 🎉
            </p>

            <p style="color: #777;">
                Ya puedes iniciar sesión y empezar a comprar o vender uniformes.
            </p>

            <hr style="margin: 20px 0;">

            <small style="color: #aaa;">
                © 2026 UniSena
            </small>

            </div>

        </body>
        </html>
        """

        correo = EmailMultiAlternatives(
            asunto,
            mensaje_texto,
            settings.EMAIL_HOST_USER,
            [correo]
        )

        correo.attach_alternative(mensaje_html, "text/html")
        correo.send()

        messages.success(request, "Usuario registrado correctamente.")

        return redirect("/")

    return render(request, "registro.html")

def recuperar_password(request):
    
    if request.method == "POST":
        correo = request.POST.get("correo")

        try:
            usuario = Usuario.objects.get(correo=correo)

            # 🔢 generar código de 6 dígitos
            codigo = str(random.randint(100000, 999999))

            usuario.reset_codigo = codigo
            usuario.reset_codigo_fecha = now()
            usuario.save()

            # 📩 correo bonito
            mensaje_html = f"""
            <div style="font-family: Arial; text-align:center;">
                <h2 style="color:#125f58;">Recuperar contraseña</h2>
                <p>Tu código es:</p>
                <h1 style="letter-spacing:5px;">{codigo}</h1>
                <p>No lo compartas con nadie</p>
            </div>
            """

            email = EmailMultiAlternatives(
                "Código de recuperación",
                "Tu código es " + codigo,
                settings.EMAIL_HOST_USER,
                [correo]
            )

            email.attach_alternative(mensaje_html, "text/html")
            email.send()
            
              # 🔴 AÑADIDO
            
            request.session["correo_reset"] = correo  # 🔴 AÑADIDO para mantener el correo en la sesión

            # 🔥 redirige a donde se pone el código
            return redirect("reset_password")

        except Usuario.DoesNotExist:
            return render(request, "recuperar.html", {"error": "Correo no registrado"})

    return render(request, "recuperar.html")

def reset_password(request):

    correo = request.session.get("correo_reset")

    if not correo:
        return redirect("recuperar")

    try:
        usuario = Usuario.objects.get(correo=correo)
    except Usuario.DoesNotExist:
        return redirect("recuperar")

    if request.method == "POST":

        accion = request.POST.get("accion")

        # 🔁 REENVIAR CÓDIGO
        if accion == "reenviar":
            import random
            from django.utils.timezone import now

            codigo = str(random.randint(100000, 999999))

            usuario.reset_codigo = codigo
            usuario.reset_codigo_fecha = now()
            usuario.reset_intentos = 0
            usuario.save()

            from django.core.mail import EmailMultiAlternatives
            from django.conf import settings

            mensaje_html = f"""
            <div style="text-align:center;">
                <h2>Nuevo código</h2>
                <h1>{codigo}</h1>
            </div>
            """

            email = EmailMultiAlternatives(
                "Nuevo código",
                "Tu código es " + codigo,
                settings.EMAIL_HOST_USER,
                [correo]
            )

            email.attach_alternative(mensaje_html, "text/html")
            email.send()

            return render(request, "reset.html", {
                "success": "Se envió un nuevo código"
            })

        # 🔐 CAMBIAR CONTRASEÑA
        elif accion == "cambiar":

            codigo = request.POST.get("codigo")
            password = request.POST.get("password")

            from django.utils.timezone import now
            from datetime import timedelta
            from django.contrib.auth.hashers import make_password

            if not usuario.reset_codigo_fecha:
                return render(request, "reset.html", {"error": "Solicita un código primero"})

            if now() > usuario.reset_codigo_fecha + timedelta(minutes=5):
                return render(request, "reset.html", {"error": "Código expirado"})

            if usuario.reset_intentos >= 3:
                return render(request, "reset.html", {"error": "Demasiados intentos"})

            if usuario.reset_codigo != codigo:
                usuario.reset_intentos += 1
                usuario.save()

                return render(request, "reset.html", {
                    "error": f"Código incorrecto ({usuario.reset_intentos}/3)"
                })

            # ✅ contraseña correcta
            usuario.password = make_password(password)
            usuario.reset_codigo = None
            usuario.reset_codigo_fecha = None
            usuario.reset_intentos = 0
            usuario.save()

            del request.session["correo_reset"]

            return redirect("login")

    return render(request, "reset.html")