from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect, render
from profiles.models import Client, DigitalProfile
from profiles.forms import BusinessProfileForm


@staff_member_required
def dashboard_home(request):
    total_clients = Client.objects.count()
    total_profiles = DigitalProfile.objects.count()
    active_profiles = DigitalProfile.objects.filter(is_active=True).count()
    inactive_profiles = DigitalProfile.objects.filter(is_active=False).count()
    context = {
        'total_clients': total_clients,
        'total_profiles': total_profiles,
        'active_profiles': active_profiles,
        'inactive_profiles': inactive_profiles,
        'clients': Client.objects.all()[:10],
        'profiles': DigitalProfile.objects.all()[:10],
        'business_profiles': DigitalProfile.objects.filter(
            profile_type=DigitalProfile.ProfileType.BUSINESS_ID
        ).select_related('organization').order_by('display_name'),
    }
    return render(request, 'dashboard.html', context)


def index_view(request):
    return render(request, 'index.html')


@staff_member_required
def create_client_view(request):
    return render(request, 'create_client.html')


@staff_member_required
def create_profile_view(request):
    form = BusinessProfileForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        form.instance.created_by = request.user
        form.save()
        return redirect('dashboard_home')
    return render(request, 'create_profile.html', {'form': form})
