import grpc
from . import translation_pb2, translation_pb2_grpc


def translate_text(text, language):
    channel = grpc.insecure_channel("localhost:50051")
    stub = translation_pb2_grpc.TranslationServiceStub(channel)

    response = stub.TranslateText(
        translation_pb2.TextRequest(text=text, language=language)
    )

    return response.translated_text