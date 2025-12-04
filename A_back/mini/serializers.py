from rest_framework import serializers

class LoginWithCodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=8)
