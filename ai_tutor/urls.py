from django.urls import path
from . import views, document_views

app_name = 'ai_tutor'

urlpatterns = [
    # Core Tutor Chat
    path('', views.tutor_workspace_view, name='workspace'),
    path('c/<int:conversation_id>/', views.tutor_workspace_view, name='conversation_detail'),
    path('c/new/', views.create_conversation_view, name='create_conversation'),
    path('c/<int:conversation_id>/send/', views.send_message_api, name='send_message'),
    path('c/<int:conversation_id>/delete/', views.delete_conversation_api, name='delete_conversation'),
    path('messages/<int:message_id>/save/', views.toggle_save_message_api, name='toggle_save_message'),
    path('saved/', views.saved_answers_view, name='saved_answers'),

    # Phase 3: AI Chat with PDF & Study Materials
    path('documents/', document_views.document_list_view, name='document_list'),
    path('documents/<int:document_id>/', document_views.document_chat_view, name='document_chat'),
    path('documents/<int:document_id>/ask/', document_views.document_ask_api, name='document_ask'),
    path('documents/<int:document_id>/action/', document_views.document_action_api, name='document_action'),
    path('documents/<int:document_id>/delete/', document_views.document_delete_view, name='document_delete'),
]
