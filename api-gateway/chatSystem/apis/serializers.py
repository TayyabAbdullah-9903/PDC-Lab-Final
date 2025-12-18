from rest_framework import serializers
from .models import UserProfile, ChatMessage


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['username', 'language']


class SendTextSerializer(serializers.Serializer):
    sender = serializers.CharField(max_length=50)
    receiver = serializers.CharField(max_length=50)
    text = serializers.CharField()
    target_language = serializers.CharField(max_length=10)


class SendAudioSerializer(serializers.Serializer):
    sender = serializers.CharField(max_length=50)
    receiver = serializers.CharField(max_length=50)
    audio = serializers.CharField()  # base64 encoded audio data or raw string


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = '__all__'
