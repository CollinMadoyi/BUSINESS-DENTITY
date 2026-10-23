from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render


def admin_login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None and user.is_active:
            login(request, user)
            return redirect('dashboard_home')
        messages.error(request, 'Invalid email or password.')
    return render(request, 'admin_login.html')


def admin_logout_view(request):
    logout(request)
    return redirect('admin_login')
