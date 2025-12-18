from django.urls import path
from . import views

urlpatterns = [
    path('set-language/', views.set_language),
    path('send-text/', views.send_text),
    path('send-audio/', views.send_audio),
    path('history/', views.chat_history),
    path('send-text-rest/', views.send_text_rest_only),
    path('send-audio-rest/', views.send_audio_rest_only),
]
