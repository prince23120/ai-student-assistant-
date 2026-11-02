import os
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.contrib import messages
from accounts.decorators import student_required
from study_planner.models import Subject
from dashboard.models import RecentActivity
from .models import StudyMaterial, DocumentChunk, DocumentConversation, DocumentChatMessage, AIConversation
from .document_parser import parse_document_file, chunk_document_pages
from .rag_engine import ask_document_rag, generate_document_summary, generate_document_notes, generate_document_mcqs

@login_required
@student_required
def document_list_view(request):
    """
    Renders the study materials library where students can upload and manage documents.
    """
    student = request.user
    documents = StudyMaterial.objects.filter(student=student)
    subjects = Subject.objects.filter(student=student)

    if request.method == 'POST':
        uploaded_file = request.FILES.get('document_file')
        title = request.POST.get('title', '').strip()
        subject_id = request.POST.get('subject_id')

        if not uploaded_file:
            messages.error(request, "Please select a file to upload.")
            return redirect('ai_tutor:document_list')

        # Validate file size (25MB limit)
        if uploaded_file.size > 25 * 1024 * 1024:
            messages.error(request, "File size exceeds the 25MB limit.")
            return redirect('ai_tutor:document_list')

        # Determine file type
        name, ext = os.path.splitext(uploaded_file.name)
        ext_clean = ext.lower().replace('.', '')
        if ext_clean not in ['pdf', 'docx', 'pptx', 'ppt', 'txt', 'md']:
            messages.error(request, f"Unsupported file type (.{ext_clean}). Supported: PDF, DOCX, PPTX, TXT.")
            return redirect('ai_tutor:document_list')

        mapped_type = 'pptx' if ext_clean in ['pptx', 'ppt'] else ('txt' if ext_clean == 'md' else ext_clean)
        doc_title = title if title else name.replace('_', ' ').replace('-', ' ').title()

        subject = None
        if subject_id:
            subject = Subject.objects.filter(id=subject_id, student=student).first()

        # Save document
        doc = StudyMaterial.objects.create(
            student=student,
            subject=subject,
            title=doc_title,
            file=uploaded_file,
            file_type=mapped_type,
            file_size_bytes=uploaded_file.size
        )

        # Parse & Chunk Document
        try:
            pages = parse_document_file(doc.file.path, ext_clean)
            doc.page_count = max(1, len(pages))
            chunks_data = chunk_document_pages(pages)

            chunk_objs = [
                DocumentChunk(
                    document=doc,
                    chunk_index=c['chunk_index'],
                    page_number=c['page_number'],
                    content=c['content']
                )
                for c in chunks_data
            ]
            DocumentChunk.objects.bulk_create(chunk_objs)
            doc.is_processed = True
            doc.save()

            RecentActivity.objects.create(
                user=student,
                title=f"Uploaded Document: {doc.title}",
                category="DOCUMENT",
                icon="file-text"
            )
            messages.success(request, f"Document '{doc.title}' successfully processed ({doc.page_count} pages/slides ready for RAG chat)!")
            return redirect('ai_tutor:document_chat', document_id=doc.id)

        except Exception as e:
            messages.warning(request, f"Uploaded '{doc.title}', but parsing encountered an issue: {str(e)}")
            return redirect('ai_tutor:document_chat', document_id=doc.id)

    context = {
        'documents': documents,
        'subjects': subjects,
    }
    return render(request, 'ai_tutor/document_list.html', context)


@login_required
@student_required
def document_chat_view(request, document_id):
    """
    Interactive RAG workspace: side-by-side document metadata, summary tools, and live PDF chat.
    """
    student = request.user
    document = get_object_or_404(StudyMaterial, id=document_id, student=student)

    # Get or create active document conversation
    conversation, _ = DocumentConversation.objects.get_or_create(
        student=student,
        document=document,
        defaults={'title': f"Chat: {document.title}"}
    )

    chat_messages = conversation.messages.all()

    context = {
        'document': document,
        'conversation': conversation,
        'chat_messages': chat_messages,
        'chunks_count': document.chunks.count(),
    }
    return render(request, 'ai_tutor/document_chat.html', context)


@login_required
@student_required
@require_POST
def document_ask_api(request, document_id):
    """
    RAG Chat API: Retrieves relevant document chunks and answers with page citations.
    """
    student = request.user
    document = get_object_or_404(StudyMaterial, id=document_id, student=student)

    try:
        data = json.loads(request.body)
        query = data.get('query', '').strip()
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")

    if not query:
        return JsonResponse({'status': 'error', 'message': 'Query cannot be empty'}, status=400)

    conversation, _ = DocumentConversation.objects.get_or_create(
        student=student,
        document=document,
        defaults={'title': f"Chat: {document.title}"}
    )

    # Save User message
    user_msg = DocumentChatMessage.objects.create(
        conversation=conversation,
        role=DocumentChatMessage.Role.USER,
        content=query
    )

    # Create dummy AIConversation proxy for service compatibility
    ai_conv_proxy, _ = AIConversation.objects.get_or_create(
        student=student,
        title=f"Doc RAG: {document.title}",
        defaults={'mode': AIConversation.Mode.TUTOR, 'subject': document.subject}
    )

    # Run RAG
    ai_answer, citations = ask_document_rag(document, query, ai_conv_proxy)

    # Save Assistant message
    assistant_msg = DocumentChatMessage.objects.create(
        conversation=conversation,
        role=DocumentChatMessage.Role.ASSISTANT,
        content=ai_answer,
        page_citations=citations
    )

    RecentActivity.objects.create(
        user=student,
        title=f"Document Query on '{document.title[:25]}'",
        category="DOC_CHAT",
        icon="file-question"
    )

    return JsonResponse({
        'status': 'ok',
        'answer': ai_answer,
        'citations': citations,
        'assistant_message_id': assistant_msg.id
    })


@login_required
@student_required
@require_POST
def document_action_api(request, document_id):
    """
    Generates Summaries, Notes, or MCQs from uploaded document.
    """
    student = request.user
    document = get_object_or_404(StudyMaterial, id=document_id, student=student)
    action = request.POST.get('action')

    ai_conv_proxy, _ = AIConversation.objects.get_or_create(
        student=student,
        title=f"Doc RAG: {document.title}",
        defaults={'mode': AIConversation.Mode.TUTOR, 'subject': document.subject}
    )

    if action == 'summary':
        content = generate_document_summary(document, ai_conv_proxy)
        document.summary = content
        document.save()
    elif action == 'mcqs':
        content = generate_document_mcqs(document, ai_conv_proxy, count=5)
    elif action == 'notes':
        content = generate_document_notes(document, ai_conv_proxy)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid action'}, status=400)

    return JsonResponse({'status': 'ok', 'content': content, 'action': action})


@login_required
@student_required
@require_POST
def document_delete_view(request, document_id):
    """
    Deletes an uploaded document and cleans its physical file and chunks.
    """
    student = request.user
    document = get_object_or_404(StudyMaterial, id=document_id, student=student)
    title = document.title

    if document.file:
        try:
            if os.path.isfile(document.file.path):
                os.remove(document.file.path)
        except Exception:
            pass

    document.delete()
    messages.success(request, f"Document '{title}' deleted.")
    return redirect('ai_tutor:document_list')
