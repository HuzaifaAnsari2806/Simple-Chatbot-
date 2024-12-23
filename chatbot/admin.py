from django.contrib import admin
from .models import Lead, Question, UserInteraction


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created_at")
    search_fields = ("name", "email")


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "next_question", "created_at")
    search_fields = ("text",)


@admin.register(UserInteraction)
class UserInteractionAdmin(admin.ModelAdmin):
    list_display = ("lead", "question", "timestamp")
    list_filter = ("lead", "question")
