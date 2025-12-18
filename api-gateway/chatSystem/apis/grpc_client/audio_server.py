import grpc
from concurrent import futures
import sys
from pathlib import Path
from .audio_pb2 import AudioResponse
from . import audio_pb2_grpc


class AudioService(audio_pb2_grpc.AudioServiceServicer):

    def ProcessAudio(self, request, context):
        """
        Process audio by simulating compression/processing.
        In a real system, this would do actual audio processing.
        """
        # Simulate audio processing by reversing the bytes
        processed_audio = request.audio[::-1]
        
        return AudioResponse(audio=processed_audio)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    audio_pb2_grpc.add_AudioServiceServicer_to_server(
        AudioService(), server
    )
    server.add_insecure_port("[::]:50052")
    server.start()
    print("Audio gRPC Service running on port 50052")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
