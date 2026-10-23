from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    AdminLoginView,
    AdminLogoutView,
    AdminProfileCreateAPIView,
    AdminProfileListAPIView,
    PublicProfileAPIView,
    PublicVCardAPIView,
)

urlpatterns = [
    path('admin/login/', AdminLoginView.as_view(), name='admin_login_api'),
    path('admin/logout/', AdminLogoutView.as_view(), name='admin_logout_api'),
    path('admin/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('admin/profiles/', AdminProfileListAPIView.as_view(), name='admin_profiles'),
    path('admin/profiles/create/', AdminProfileCreateAPIView.as_view(), name='admin_profile_create'),
    path('public/profile/<slug:slug>/', PublicProfileAPIView.as_view(), name='public_profile_api'),
    path('public/profile/<slug:slug>/vcard/', PublicVCardAPIView.as_view(), name='public_vcard'),
]
