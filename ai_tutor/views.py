import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from accounts.decorators import student_required
from study_planner.models import Subject
from dashboard.models import RecentActivity
from .models import AIConversation, ChatMessage, SavedAnswer
from .services import get_ai_tutor_response

@login_required
@student_required
def tutor_workspace_view(request, conversation_id=None):
    student = request.user
    conversations = AIConversation.objects.filter(student=student)
    subjects = Subject.objects.filter(student=student)

    active_conversation = None
    if conversation_id:
        active_conversation = get_object_or_404(AIConversation, id=conversation_id, student=student)
    elif conversations.exists():
        active_conversation = conversations.first()

    chat_messages = []
    if active_conversation:
        chat_messages = active_conversation.messages.all()

    context = {
        'conversations': conversations,
        'active_conversation': active_conversation,
        'chat_messages': chat_messages,
        'subjects': subjects,
        'modes': AIConversation.Mode.choices,
        'languages': AIConversation.Language.choices,
    }
    return render(request, 'ai_tutor/tutor_workspace.html', context)


@login_required
@student_required
@require_POST
def create_conversation_view(request):
    mode = request.POST.get('mode', AIConversation.Mode.TUTOR)
    language = request.POST.get('language', AIConversation.Language.ENGLISH)
    subject_id = request.POST.get('subject_id')

    subject = None
    if subject_id:
        subject = Subject.objects.filter(id=subject_id, student=request.user).first()

    conv = AIConversation.objects.create(
        student=request.user,
        title="New Study Session",
        mode=mode,
        language=language,
        subject=subject
    )
    return redirect('ai_tutor:conversation_detail', conversation_id=conv.id)


@login_required
@student_required
@require_POST
def send_message_api(request, conversation_id):
    conv = get_object_or_404(AIConversation, id=conversation_id, student=request.user)

    try:
        data = json.loads(request.body)
        user_text = data.get('message', '').strip()
        mode = data.get('mode')
        language = data.get('language')
        subject_id = data.get('subject_id')
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")

    if not user_text:
        return JsonResponse({'status': 'error', 'message': 'Message cannot be empty'}, status=400)

    # Update conversation settings if changed
    if mode and mode in dict(AIConversation.Mode.choices):
        conv.mode = mode
    if language and language in dict(AIConversation.Language.choices):
        conv.language = language
    if subject_id:
        conv.subject = Subject.objects.filter(id=subject_id, student=request.user).first()

    # Save User message
    user_msg = ChatMessage.objects.create(
        conversation=conv,
        role=ChatMessage.Role.USER,
        content=user_text
    )

    # Update conversation title if still default
    if conv.title == "New Study Session" or conv.messages.count() <= 2:
        words = user_text.split()[:6]
        conv.title = " ".join(words) + ("..." if len(user_text.split()) > 6 else "")

    conv.save()

    # Generate AI Tutor response
    ai_response_text = get_ai_tutor_response(conv, user_text)

    # Save Assistant message
    assistant_msg = ChatMessage.objects.create(
        conversation=conv,
        role=ChatMessage.Role.ASSISTANT,
        content=ai_response_text
    )

    # Record Activity
    RecentActivity.objects.create(
        user=request.user,
        title=f"Asked AI Tutor: {conv.title[:35]}",
        category="AI_TUTOR",
        icon="bot"
    )

    return JsonResponse({
        'status': 'ok',
        'response': ai_response_text,
        'user_message_id': user_msg.id,
        'assistant_message_id': assistant_msg.id,
        'conversation_title': conv.title,
    })


@login_required
@student_required
@require_POST
def delete_conversation_api(request, conversation_id):
    conv = get_object_or_404(AIConversation, id=conversation_id, student=request.user)
    conv.delete()
    messages.success(request, "Conversation deleted.")
    return redirect('ai_tutor:workspace')


@login_required
@student_required
@require_POST
def toggle_save_message_api(request, message_id):
    msg = get_object_or_404(ChatMessage, id=message_id, conversation__student=request.user)
    msg.is_saved = not msg.is_saved
    msg.save()

    if msg.is_saved:
        SavedAnswer.objects.get_or_create(
            student=request.user,
            message=msg,
            defaults={
                'title': msg.conversation.title,
                'subject': msg.conversation.subject
            }
        )
    else:
        SavedAnswer.objects.filter(student=request.user, message=msg).delete()

    return JsonResponse({'status': 'ok', 'is_saved': msg.is_saved})


@login_required
@student_required
def saved_answers_view(request):
    answers = SavedAnswer.objects.filter(student=request.user).select_related('message', 'subject')
    return render(request, 'ai_tutor/saved_answers.html', {'saved_answers': answers})
