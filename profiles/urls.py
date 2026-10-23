from django.urls import path
from .views import (
    business_profile_view,
    download_profile_card_view,
    edit_business_profile_view,
    public_profile_api,
    public_profile_view,
    profile_share_image_view,
    public_profile_view_by_id,
)

urlpatterns = [
    path('id/<slug:slug>/', public_profile_view, name='public_profile'),
    path('item/<uuid:public_id>/', public_profile_view_by_id, name='profile_by_public_id'),
    path('business/<slug:slug>/', business_profile_view, name='business_profile'),
    path('card/<slug:slug>/printable.pdf', download_profile_card_view, name='download_profile_card'),
    path('card/<slug:slug>/share.png', profile_share_image_view, name='profile_share_image'),
    path('business/<slug:slug>/edit/', edit_business_profile_view, name='edit_business_profile'),
    path('student/<slug:slug>/', public_profile_view, name='student_profile'),
    path('portfolio/<slug:slug>/', public_profile_view, name='portfolio_profile'),
    path('company/<slug:slug>/', public_profile_view, name='company_profile'),
    path('api/public/profile/<slug:slug>/', public_profile_api, name='public_profile_api'),
]
