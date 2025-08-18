from rest_framework import serializers
from .models import Emprunt

class EmpruntSerializer(serializers.ModelSerializer):
    class Meta:
        model = Emprunt
        fields = "__all__"
