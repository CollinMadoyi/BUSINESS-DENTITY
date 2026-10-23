from rest_framework import serializers
from profiles.models import Client, DigitalProfile

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DigitalProfile
        fields = '__all__'
