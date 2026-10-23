from urllib.parse import quote

from django.conf import settings
from django.http import FileResponse, JsonResponse
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET
from .forms import BusinessProfileForm
from .models import DigitalProfile, public_profile_path
from .card_pdf import render_profile_card
from .profile_share_image import render_profile_share_image


def _public_profile_context(request, profile):
    site_url = getattr(settings, 'SITE_URL', '').rstrip('/')
    profile_path = public_profile_path(profile)
    image_path = reverse('profile_share_image', kwargs={'slug': profile.slug})
    canonical_url = f'{site_url}{profile_path}' if site_url else request.build_absolute_uri(profile_path)
    share_image_url = f'{site_url}{image_path}' if site_url else request.build_absolute_uri(image_path)
    organization_name = profile.organization.name if profile.organization else ''
    description = profile.bio or f'Digital profile for {profile.display_name}'
    if organization_name and not profile.bio:
        description += f' at {organization_name}'
    whatsapp_text = f"View {profile.display_name}'s digital profile: {canonical_url}"
    return {
        'profile': profile,
        'canonical_url': canonical_url,
        'share_image_url': share_image_url,
        'share_description': description[:300],
        'whatsapp_share_url': f'https://wa.me/?text={quote(whatsapp_text)}',
    }


def public_profile_view(request, slug):
    profile = get_object_or_404(
        DigitalProfile.objects.select_related('organization'),
        slug=slug,
        is_active=True,
    )
    return render(request, 'profile.html', _public_profile_context(request, profile))


def public_profile_view_by_id(request, public_id):
    profile = get_object_or_404(
        DigitalProfile.objects.select_related('organization'),
        public_id=public_id,
        is_active=True,
    )
    return render(request, 'profile.html', _public_profile_context(request, profile))


def business_profile_view(request, slug):
    profile = get_object_or_404(
        DigitalProfile.objects.select_related('organization'),
        slug=slug,
        profile_type=DigitalProfile.ProfileType.BUSINESS_ID,
        is_active=True,
    )
    return render(request, 'profile.html', _public_profile_context(request, profile))


def profile_share_image_view(request, slug):
    profile = get_object_or_404(
        DigitalProfile.objects.select_related('organization'),
        slug=slug,
        is_active=True,
    )
    response = HttpResponse(render_profile_share_image(profile), content_type='image/png')
    response['Cache-Control'] = 'no-store'
    return response


def download_profile_card_view(request, slug):
    profile = get_object_or_404(
        DigitalProfile.objects.select_related('organization'),
        slug=slug,
        is_active=True,
    )
    return FileResponse(
        render_profile_card(profile),
        as_attachment=True,
        filename=f'{profile.slug}-printable-card.pdf',
        content_type='application/pdf',
    )


@login_required
def edit_business_profile_view(request, slug):
    profile = get_object_or_404(
        DigitalProfile,
        slug=slug,
        profile_type=DigitalProfile.ProfileType.BUSINESS_ID,
    )
    is_profile_owner = (
        profile.created_by_id == request.user.pk
        or profile.client.created_by_id == request.user.pk
    )
    if not request.user.is_staff and not is_profile_owner:
        raise PermissionDenied
    form = BusinessProfileForm(
        request.POST or None,
        request.FILES or None,
        instance=profile,
    )
    if request.method == 'POST' and form.is_valid():
        form.save()
        if not request.user.is_staff:
            return redirect('public_profile', slug=profile.slug)
        return redirect('dashboard_home')
    return render(request, 'edit_profile.html', {'form': form, 'profile': profile})


@require_GET
def public_profile_api(request, slug):
    profile = get_object_or_404(DigitalProfile, slug=slug, is_active=True)
    data = {
        'id': profile.id,
        'name': profile.display_name,
        'title': profile.title,
        'organization': getattr(profile.organization, 'name', None),
        'email': profile.email,
        'phone': profile.phone,
        'website': profile.website,
        'address': profile.address,
        'google_maps_url': profile.google_maps_url,
        'bio': profile.bio,
        'slug': profile.slug,
        'color_theme': profile.color_theme,
        'profile_photo': profile.profile_photo.url if profile.profile_photo else '',
    }
    return JsonResponse(data)
