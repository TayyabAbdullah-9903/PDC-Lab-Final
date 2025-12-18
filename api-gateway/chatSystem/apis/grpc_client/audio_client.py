import grpc
from . import audio_pb2, audio_pb2_grpc


def process_audio(audio_bytes):
    """
    Send audio bytes to the Audio gRPC service for processing.
    
    Args:
        audio_bytes: Raw audio data as bytes
        
    Returns:
        Processed audio bytes
    """
    channel = grpc.insecure_channel("localhost:50052")
    stub = audio_pb2_grpc.AudioServiceStub(channel)

    response = stub.ProcessAudio(
        audio_pb2.AudioRequest(audio=audio_bytes)
    )

    return response.audio
