from django.contrib import admin
from .models import AIConversation, ChatMessage, SavedAnswer

class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ('created_at',)

@admin.register(AIConversation)
class AIConversationAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'subject', 'mode', 'language', 'updated_at')
    list_filter = ('mode', 'language', 'updated_at')
    search_fields = ('title', 'student__username', 'subject__name')
    inlines = [ChatMessageInline]

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'role', 'is_saved', 'created_at')
    list_filter = ('role', 'is_saved', 'created_at')
    search_fields = ('content', 'conversation__title', 'conversation__student__username')

@admin.register(SavedAnswer)
class SavedAnswerAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'subject', 'created_at')
    search_fields = ('title', 'student__username', 'notes')
