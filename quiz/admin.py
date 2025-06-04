from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, Round, Topic, Question, Answer, UserRound

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'full_name', 'score', 'is_email_verified')
    search_fields = ('username', 'full_name')
    list_filter = ('is_email_verified',)
    
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('username', 'full_name', 'email', 'avatar')
        }),
        (_('Статистика'), {
            'fields': ('score', 'is_email_verified')
        }),
        (_('Права доступа'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Важные даты'), {
            'fields': ('last_login', 'date_joined')
        }),
    )

class RoundAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'start_time', 'end_time')
    list_filter = ('start_time', 'end_time')
    search_fields = ('title',)
    ordering = ('order',)
    
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('title', 'order')
        }),
        (_('Временные рамки'), {
            'fields': ('start_time', 'end_time')
        }),
    )

class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'round')
    list_filter = ('round',)
    search_fields = ('title',)
    raw_id_fields = ('round',)
    
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('round', 'title')
        }),
    )

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'topic', 'score', 'answer_type')
    list_filter = ('topic', 'answer_type')
    search_fields = ('text',)
    raw_id_fields = ('topic',)
    
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('topic', 'text', 'score', 'answer_type')
        }),
        (_('Медиа файлы'), {
            'fields': ('image', 'image2', 'audio')
        }),
        (_('Правильный ответ'), {
            'fields': ('correct_answer',)
        }),
        (_('Варианты ответов'), {
            'fields': ('option_1', 'option_2', 'option_3', 'option_4', 'option_5'),
            'classes': ('collapse',)
        }),
    )

class AnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'selected_answer', 'is_correct', 'is_passed', 'answered_at')
    list_filter = ('is_correct', 'is_passed', 'answered_at')
    search_fields = ('user__username', 'question__text')
    raw_id_fields = ('user', 'question', 'user_round')
    
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('user', 'question', 'user_round')
        }),
        (_('Ответ'), {
            'fields': ('selected_answer', 'is_correct', 'is_passed')
        }),
        (_('Время'), {
            'fields': ('answered_at', 'time_spent')
        }),
    )

class UserRoundAdmin(admin.ModelAdmin):
    list_display = ('user', 'round', 'started_at', 'ended_at', 'score', 'duration')
    list_filter = ('round', 'started_at', 'ended_at')
    search_fields = ('user__username', 'round__title')
    raw_id_fields = ('user', 'round')
    
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('user', 'round')
        }),
        (_('Результаты'), {
            'fields': ('score',)
        }),
        (_('Время'), {
            'fields': ('started_at', 'ended_at', 'duration')
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Round, RoundAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(UserRound, UserRoundAdmin)