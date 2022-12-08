# ------------------------------------------------------------------------------------------------------
# Created By  : Pablo Doñate y Adnana Dragut
# Created Date: 02/12/2022
# version ='1.0'
# ------------------------------------------------------------------------------------------------------
# File: urls.py
# ------------------------------------------------------------------------------------------------------
""" Fichero que contiene las urls del proyecto """
# ------------------------------------------------------------------------------------------------------
from django.contrib import admin
from django.urls import path
from django.urls import include
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', RedirectView.as_view(url='/cultivos/', permanent=True)),
    path('admin/', admin.site.urls),
    path('cultivos/', include('cultivos.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', views.signup, name="register"),
    path("password_reset", views.password_reset_request, name="password_reset"),
    path('reset/<uidb64>/<token>', views.password_confirm_request, name='password_reset_confirm'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete')
]
