# ------------------------------------------------------------------------------------------------------
# Created By  : Pablo Doñate y Adnana Dragut
# Created Date: 02/12/2022
# version ='1.0'
# ------------------------------------------------------------------------------------------------------
# File: views.py
# ------------------------------------------------------------------------------------------------------
""" Fichero que contiene las vistas del proyecto """
# ------------------------------------------------------------------------------------------------------
from django.shortcuts import  render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib import auth
from django.contrib import messages
from django.core.mail import send_mail, BadHeaderError
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.db.models.query_utils import Q
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str

#Función que permite determinar si un agricultor está dado de alta
def agricultorExist(_login):
    return User.objects.filter(username = _login).exists()

#Función que permite registrar un nuevo usuario agricultor
def signup(request):
    if request.method == "POST":
        agricultorName = request.POST["username"]
        agricultorEmail = request.POST['email']

        if not agricultorExist(agricultorName):
            if request.POST['password1'] == request.POST['password2']:
                user = User.objects.create_user(username=agricultorName, email=agricultorEmail, password=request.POST["password1"])
                agricultor = user.agricultor
                agricultor.email = agricultorEmail
                agricultor.save()
                auth.login(request,user)
                messages.success(request, 'El registro se ha llevado acabo de forma exitosa.')
                return redirect('https://adnana.pythonanywhere.com/cultivos/')
            else:
                messages.error(request, 'Different passwords have been entered')
        else:
            messages.error(request, 'User Already Exists')
        return render(request,'registration/register.html')
    else:
        return render(request,'registration/register.html')

#Función que permite solicitar el reseteo de la contraseña de un usuario
def password_reset_request(request):
    if request.method == 'POST':
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            user_email = password_reset_form.cleaned_data['email']
            associated_user = User.objects.filter(Q(email=user_email))[0]
            sourceFile = open('email.txt', 'w')
            print(associated_user, file = sourceFile)
            sourceFile.close()
            if associated_user:
                subject = "Password Reset Requested"
                email_template_name = "registration/password_reset_email.html"
                c = {
                    'email': associated_user.email,
                    'domain': 'adnana.pythonanywhere.com',
                    'uid': urlsafe_base64_encode(force_bytes(associated_user.pk)),
                    'user': associated_user,
                    'token': default_token_generator.make_token(associated_user),
                    "protocol": 'https' if request.is_secure() else 'http'
                }
                email = render_to_string(email_template_name, c)
                try:
                    send_mail(subject, email, 'agrohelpsystem@gmail.com' , [associated_user.email], fail_silently=False)
                except BadHeaderError:
                    messages.error(request, 'Invalid header found.')
                    return redirect('registration/password_reset.html')
                return redirect ("/password_reset/done/")
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="registration/password_reset.html", context={"password_reset_form": password_reset_form})

#Función que permite resetear la contraseña de un usuario
def password_confirm_request(request, uidb64, token):
    User = get_user_model()
    uid = force_str(urlsafe_base64_decode(uidb64))
    user = User.objects.get(pk=uid)

    if user is not None:
        if request.method == 'POST':
            set_password_form = SetPasswordForm(user, request.POST)
            user_pwd1 = request.POST['password1']
            user_pwd2 = request.POST['password2']
            if user_pwd1 == user_pwd2:
                user.set_password(user_pwd1)
                user.save()
                messages.success(request, 'La contraseña se ha cambiado correctamente.')
                return redirect ("/reset/done")
            else:
                messages.error(request, 'Different passwords have been entered')

        set_password_form = SetPasswordForm(user)
        return render(request=request, template_name="registration/password_reset_confirm.html", context={"set_password_form": set_password_form})
    else:
        messages.error(request, 'Something went wrong, try again later')
    return redirect('registration/password_reset.html')


