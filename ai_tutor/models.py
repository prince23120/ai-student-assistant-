from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class AIConversation(models.Model):
    class Mode(models.TextChoices):
        TUTOR = 'TUTOR', _('Academic Concept Tutor')
        CODE_DEBUG = 'CODE_DEBUG', _('Code Debugger & Explainer')
        EXAM_5_MARKS = 'EXAM_5_MARKS', _('5-Mark Exam Answer')
        EXAM_10_MARKS = 'EXAM_10_MARKS', _('10-Mark Exam Answer')
        SIMPLIFY = 'SIMPLIFY', _('Explain Simply / ELI5')
        NOTES = 'NOTES', _('Quick Revision Notes')

    class Language(models.TextChoices):
        ENGLISH = 'en', _('English')
        HINDI = 'hi', _('Hindi (हिंदी)')
        BILINGUAL = 'hinglish', _('Hinglish / Bilingual')

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ai_conversations'
    )
    subject = models.ForeignKey(
        'study_planner.Subject',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ai_conversations'
    )
    title = models.CharField(max_length=255, default='New Discussion')
    mode = models.CharField(
        max_length=30,
        choices=Mode.choices,
        default=Mode.TUTOR
    )
    language = models.CharField(
        max_length=15,
        choices=Language.choices,
        default=Language.ENGLISH
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.title} ({self.student.username})"


class ChatMessage(models.Model):
    class Role(models.TextChoices):
        USER = 'user', _('User')
        ASSISTANT = 'assistant', _('AI Tutor')
        SYSTEM = 'system', _('System')

    conversation = models.ForeignKey(
        AIConversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    role = models.CharField(
        max_length=15,
        choices=Role.choices,
        default=Role.USER
    )
    content = models.TextField()
    is_saved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"[{self.role}] {self.content[:40]}..."


class SavedAnswer(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_answers'
    )
    message = models.ForeignKey(
        ChatMessage,
        on_delete=models.CASCADE,
        related_name='saved_instances'
    )
    subject = models.ForeignKey(
        'study_planner.Subject',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='saved_answers'
    )
    title = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Saved: {self.title} by {self.student.username}"


class StudyMaterial(models.Model):
    class FileType(models.TextChoices):
        PDF = 'pdf', _('PDF Document')
        DOCX = 'docx', _('Word Document')
        PPTX = 'pptx', _('PowerPoint Slides')
        TXT = 'txt', _('Plain Text / Markdown')

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='study_materials'
    )
    subject = models.ForeignKey(
        'study_planner.Subject',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='study_materials'
    )
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='study_materials/%Y/%m/')
    file_type = models.CharField(
        max_length=10,
        choices=FileType.choices,
        default=FileType.PDF
    )
    file_size_bytes = models.PositiveIntegerField(default=0)
    page_count = models.PositiveIntegerField(default=1)
    summary = models.TextField(blank=True)
    key_topics = models.JSONField(default=list, blank=True)
    is_processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_file_type_display()})"


class DocumentChunk(models.Model):
    document = models.ForeignKey(
        StudyMaterial,
        on_delete=models.CASCADE,
        related_name='chunks'
    )
    chunk_index = models.PositiveIntegerField()
    page_number = models.PositiveIntegerField(default=1)
    content = models.TextField()
    keywords = models.TextField(blank=True)

    class Meta:
        ordering = ['chunk_index']
        indexes = [
            models.Index(fields=['document', 'page_number']),
        ]

    def __str__(self):
        return f"{self.document.title} - Ch {self.chunk_index} (p. {self.page_number})"


class DocumentConversation(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='document_conversations'
    )
    document = models.ForeignKey(
        StudyMaterial,
        on_delete=models.CASCADE,
        related_name='conversations'
    )
    title = models.CharField(max_length=255, default='Chat with Document')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.title} on {self.document.title}"


class DocumentChatMessage(models.Model):
    class Role(models.TextChoices):
        USER = 'user', _('User')
        ASSISTANT = 'assistant', _('AI Assistant')

    conversation = models.ForeignKey(
        DocumentConversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    role = models.CharField(
        max_length=15,
        choices=Role.choices,
        default=Role.USER
    )
    content = models.TextField()
    page_citations = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"[{self.role}] {self.content[:40]}..."
