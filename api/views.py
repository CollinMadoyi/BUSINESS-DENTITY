from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from profiles.models import DigitalProfile
from .serializers import ClientSerializer, ProfileSerializer


def _escape_vcard_value(value):
    return (
        str(value)
        .replace('\\', '\\\\')
        .replace('\r\n', '\\n')
        .replace('\r', '\\n')
        .replace('\n', '\\n')
        .replace(';', '\\;')
        .replace(',', '\\,')
    )


class AdminLoginView(TokenObtainPairView):
    permission_classes = [AllowAny]

class AdminLogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        return Response({'detail': 'Logged out successfully.'}, status=status.HTTP_200_OK)

class AdminProfileListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        profiles = DigitalProfile.objects.all()
        serializer = ProfileSerializer(profiles, many=True)
        return Response(serializer.data)

class AdminProfileCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = ProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PublicProfileAPIView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, slug):
        profile = get_object_or_404(DigitalProfile, slug=slug, is_active=True)
        return Response(ProfileSerializer(profile).data)

class PublicVCardAPIView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, slug):
        profile = get_object_or_404(DigitalProfile, slug=slug, is_active=True)
        lines = [
            'BEGIN:VCARD',
            'VERSION:3.0',
            f'FN:{_escape_vcard_value(profile.display_name)}',
        ]
        if profile.first_name or profile.last_name:
            lines.append(
                f'N:{_escape_vcard_value(profile.last_name)};'
                f'{_escape_vcard_value(profile.first_name)};;;'
            )
        if profile.organization:
            lines.append(f'ORG:{_escape_vcard_value(profile.organization.name)}')
        if profile.phone:
            lines.append(f'TEL;TYPE=CELL:{_escape_vcard_value(profile.phone)}')
        if profile.email:
            lines.append(f'EMAIL:{_escape_vcard_value(profile.email)}')
        if profile.website:
            lines.append(f'URL:{_escape_vcard_value(profile.website)}')
        if profile.address:
            lines.append(f'ADR;TYPE=WORK:;;{_escape_vcard_value(profile.address)};;;;')
        lines.append('END:VCARD')
        vcard = '\r\n'.join(lines) + '\r\n'
        response = HttpResponse(vcard, content_type='text/vcard; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{profile.slug}.vcf"'
        return response
