import time
import base64
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import UserProfile, ChatMessage
from .serializers import (
    UserProfileSerializer,
    SendTextSerializer,
    SendAudioSerializer,
    ChatMessageSerializer
)
from .grpc_client.translate_client import translate_text
from .grpc_client.audio_client import process_audio



@api_view(['POST'])
def set_language(request):
    serializer = UserProfileSerializer(data=request.data)
    if serializer.is_valid():
        user, _ = UserProfile.objects.update_or_create(
            username=serializer.validated_data['username'],
            defaults={'language': serializer.validated_data['language']}
        )
        return Response(
            {"message": "Language set successfully"},
            status=status.HTTP_200_OK
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def send_text(request):
    serializer = SendTextSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    start_time = time.perf_counter()

    translated = translate_text(
        serializer.validated_data['text'],
        serializer.validated_data['target_language']
    )

    end_time = time.perf_counter()

    chat = ChatMessage.objects.create(
        sender=serializer.validated_data['sender'],
        receiver=serializer.validated_data['receiver'],
        message_type="text",
        original_message=serializer.validated_data['text'],
        translated_message=translated
    )

    return Response({
        "translated_text": translated,
        "response_time_ms": (end_time - start_time) * 1000,
        "payload_size_bytes": len(translated.encode())
    })


@api_view(['POST'])
def send_audio(request):
    serializer = SendAudioSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    start_time = time.perf_counter()

    # Convert base64 audio string to bytes
    try:
        audio_data = serializer.validated_data['audio']
        # If it's base64 encoded, decode it; otherwise use as is
        try:
            audio_bytes = base64.b64decode(audio_data)
        except:
            audio_bytes = audio_data.encode()
        
        # Process audio through gRPC service
        processed_audio_bytes = process_audio(audio_bytes)
        
        # Convert back to base64 for response
        processed_audio_b64 = base64.b64encode(processed_audio_bytes).decode()
        
    except Exception as e:
        return Response(
            {"error": f"Audio processing failed: {str(e)}"}, 
            status=500
        )

    end_time = time.perf_counter()

    ChatMessage.objects.create(
        sender=serializer.validated_data['sender'],
        receiver=serializer.validated_data['receiver'],
        message_type="audio",
        original_message=f"audio-{len(audio_bytes)}-bytes",
        translated_message=f"audio-{len(processed_audio_bytes)}-bytes"
    )

    return Response({
        "message": "Audio processed successfully",
        "processed_audio": processed_audio_b64,
        "response_time_ms": (end_time - start_time) * 1000,
        "original_size_bytes": len(audio_bytes),
        "processed_size_bytes": len(processed_audio_bytes)
    })



@api_view(['GET'])
def chat_history(request):
    messages = ChatMessage.objects.all().order_by('-timestamp')
    serializer = ChatMessageSerializer(messages, many=True)
    return Response(serializer.data)


# ============================================
# REST-ONLY ENDPOINTS (No gRPC - For Performance Comparison)
# ============================================

@api_view(['POST'])
def send_text_rest_only(request):
    """
    REST-only text translation endpoint (no gRPC).
    Translation logic performed directly in REST API for performance comparison.
    """
    serializer = SendTextSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    start_time = time.perf_counter()

    # Translation logic done in REST (no gRPC call)
    text = serializer.validated_data['text']
    target_language = serializer.validated_data['target_language']
    
    # Same translation mapping as gRPC service
    translation_mapping = {
        "ur": "ہیلو",
        "fr": "Bonjour",
        "es": "Hola"
    }
    translated = translation_mapping.get(target_language, text)

    end_time = time.perf_counter()

    ChatMessage.objects.create(
        sender=serializer.validated_data['sender'],
        receiver=serializer.validated_data['receiver'],
        message_type="text",
        original_message=text,
        translated_message=translated
    )

    return Response({
        "translated_text": translated,
        "response_time_ms": (end_time - start_time) * 1000,
        "payload_size_bytes": len(translated.encode()),
        "method": "REST-only (no gRPC)"
    })


@api_view(['POST'])
def send_audio_rest_only(request):
    """
    REST-only audio processing endpoint (no gRPC).
    Audio processing logic performed directly in REST API for performance comparison.
    """
    serializer = SendAudioSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    start_time = time.perf_counter()

    try:
        audio_data = serializer.validated_data['audio']
        
        # Convert base64 audio string to bytes
        try:
            audio_bytes = base64.b64decode(audio_data)
        except:
            audio_bytes = audio_data.encode()
        
        # Audio processing logic done in REST (no gRPC call)
        # Same processing as gRPC service: byte reversal
        processed_audio_bytes = audio_bytes[::-1]
        
        # Convert back to base64 for response
        processed_audio_b64 = base64.b64encode(processed_audio_bytes).decode()
        
    except Exception as e:
        return Response(
            {"error": f"Audio processing failed: {str(e)}"}, 
            status=500
        )

    end_time = time.perf_counter()

    ChatMessage.objects.create(
        sender=serializer.validated_data['sender'],
        receiver=serializer.validated_data['receiver'],
        message_type="audio",
        original_message=f"audio-{len(audio_bytes)}-bytes",
        translated_message=f"audio-{len(processed_audio_bytes)}-bytes"
    )

    return Response({
        "message": "Audio processed successfully (REST-only)",
        "processed_audio": processed_audio_b64,
        "response_time_ms": (end_time - start_time) * 1000,
        "original_size_bytes": len(audio_bytes),
        "processed_size_bytes": len(processed_audio_bytes),
        "method": "REST-only (no gRPC)"
    })
