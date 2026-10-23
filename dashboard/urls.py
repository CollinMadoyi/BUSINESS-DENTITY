from django.urls import path
from .views import dashboard_home, index_view, create_client_view, create_profile_view

urlpatterns = [
    path('', index_view, name='home'),
    path('dashboard/', dashboard_home, name='dashboard_home'),
    path('clients/create/', create_client_view, name='create_client'),
    path('profiles/create/', create_profile_view, name='create_profile'),
]
