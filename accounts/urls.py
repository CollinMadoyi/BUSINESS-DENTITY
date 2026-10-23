from django.contrib.auth import views as auth_views
from django.urls import path
from .views import admin_login_view, admin_logout_view

urlpatterns = [
    path('login/', admin_login_view, name='admin_login'),
    path('logout/', admin_logout_view, name='admin_logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='admin_login.html'), name='password_reset'),
]
