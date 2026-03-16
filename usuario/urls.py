from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),

    path('inicio-admin/', views.inicio_admin, name='inicio_admin'),

    path('inicio-cliente/', views.inicio_cliente, name='inicio_cliente'),

    path('inicio-vendedor/', views.inicio_vendedor, name='inicio_vendedor'),

    path('logout/', views.logout_view, name='logout'),

    path('registro/', views.registro_view, name='registro'),

]