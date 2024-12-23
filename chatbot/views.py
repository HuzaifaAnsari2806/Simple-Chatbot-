from django.shortcuts import render
from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework import viewsets
from .models import Lead, Question, UserInteraction
from .serializers import LeadSerializer, QuestionSerializer, UserInteractionSerializer


class ChatbotView(TemplateView):
    template_name = "chatbot/chat.html"


class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class UserIntViewSet(viewsets.ModelViewSet):
    queryset = UserInteraction.objects.all()
    serializer_class = UserInteractionSerializer
