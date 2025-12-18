import grpc
from concurrent import futures
import sys
from pathlib import Path
from .translation_pb2 import TextResponse
from . import translation_pb2_grpc

class TranslationService(translation_pb2_grpc.TranslationServiceServicer):

    def TranslateText(self, request, context):
        mapping = {
            "ur": "ہیلو",
            "fr": "Bonjour",
            "es": "Hola"
        }

        return TextResponse(
            translated_text=mapping.get(request.language, request.text)
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    translation_pb2_grpc.add_TranslationServiceServicer_to_server(
        TranslationService(), server
    )
    server.add_insecure_port("[::]:50051")
    server.start()
    print("Translation gRPC Service running on port 50051")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
