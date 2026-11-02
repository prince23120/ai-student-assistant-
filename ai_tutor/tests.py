import json
from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from study_planner.models import Subject
from ai_tutor.models import AIConversation, ChatMessage, SavedAnswer

class AITutorTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            username='tutorstudent',
            email='tutor@example.com',
            password='Password123!',
            role=User.Role.STUDENT,
            first_name='Alex'
        )
        self.subject = Subject.objects.create(
            student=self.student,
            name='Algorithms',
            code='CS301'
        )
        self.client.login(username='tutorstudent', password='Password123!')

    def test_workspace_view(self):
        response = self.client.get(reverse('ai_tutor:workspace'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AI Study Tutor')

    def test_create_conversation(self):
        response = self.client.post(reverse('ai_tutor:create_conversation'), {
            'mode': AIConversation.Mode.TUTOR,
            'language': AIConversation.Language.ENGLISH,
            'subject_id': self.subject.id
        })
        self.assertEqual(response.status_code, 302)
        conv = AIConversation.objects.filter(student=self.student).first()
        self.assertIsNotNone(conv)
        self.assertEqual(conv.subject, self.subject)

    def test_send_message_api(self):
        conv = AIConversation.objects.create(
            student=self.student,
            title='Test Session',
            mode=AIConversation.Mode.TUTOR,
            language=AIConversation.Language.ENGLISH,
            subject=self.subject
        )
        url = reverse('ai_tutor:send_message', kwargs={'conversation_id': conv.id})
        payload = {
            'message': 'Explain Dijkstra shortest path algorithm with time complexity',
            'mode': 'TUTOR',
            'language': 'en',
            'subject_id': self.subject.id
        }
        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'ok')
        self.assertIn('response', data)

        # Check DB messages
        self.assertEqual(conv.messages.count(), 2)  # User + Assistant
        user_msg = conv.messages.filter(role=ChatMessage.Role.USER).first()
        asst_msg = conv.messages.filter(role=ChatMessage.Role.ASSISTANT).first()
        self.assertEqual(user_msg.content, payload['message'])
        self.assertTrue(len(asst_msg.content) > 20)

    def test_toggle_save_message_and_view(self):
        conv = AIConversation.objects.create(
            student=self.student,
            title='Algorithm Analysis',
            subject=self.subject
        )
        msg = ChatMessage.objects.create(
            conversation=conv,
            role=ChatMessage.Role.ASSISTANT,
            content='### Step by step proof of Master Theorem'
        )
        url = reverse('ai_tutor:toggle_save_message', kwargs={'message_id': msg.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['is_saved'])

        saved = SavedAnswer.objects.filter(student=self.student, message=msg).first()
        self.assertIsNotNone(saved)

        # Test saved answers list view
        list_response = self.client.get(reverse('ai_tutor:saved_answers'))
        self.assertEqual(list_response.status_code, 200)
        self.assertContains(list_response, 'Master Theorem')

    def test_delete_conversation(self):
        conv = AIConversation.objects.create(student=self.student, title='To Delete')
        ChatMessage.objects.create(conversation=conv, role='user', content='Hello')
        url = reverse('ai_tutor:delete_conversation', kwargs={'conversation_id': conv.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(AIConversation.objects.filter(id=conv.id).exists())

    def test_document_upload_and_chunking(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        from ai_tutor.models import StudyMaterial, DocumentChunk

        file_content = b"Chapter 1: Graph Theory. Graphs are composed of vertices and edges. Chapter 2: Tree Traversals."
        test_file = SimpleUploadedFile("graph_notes.txt", file_content, content_type="text/plain")

        response = self.client.post(reverse('ai_tutor:document_list'), {
            'title': 'Graph Theory Notes',
            'subject_id': self.subject.id,
            'document_file': test_file
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        doc = StudyMaterial.objects.filter(student=self.student, title='Graph Theory Notes').first()
        self.assertIsNotNone(doc)
        self.assertTrue(doc.is_processed)
        self.assertTrue(doc.chunks.count() > 0)

    def test_document_rag_chat_api(self):
        from ai_tutor.models import StudyMaterial, DocumentChunk

        doc = StudyMaterial.objects.create(
            student=self.student,
            title='OS Paging Notes',
            file_type='pdf',
            page_count=2,
            is_processed=True
        )
        DocumentChunk.objects.create(
            document=doc,
            chunk_index=1,
            page_number=2,
            content="Demand paging brings a page into memory only when it is needed. Page fault happens when valid bit is 0."
        )

        url = reverse('ai_tutor:document_ask', kwargs={'document_id': doc.id})
        response = self.client.post(
            url,
            data=json.dumps({'query': 'What is demand paging?'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'ok')
        self.assertIn('answer', data)
        self.assertTrue(len(data['citations']) > 0)
        self.assertEqual(data['citations'][0]['page_number'], 2)

    def test_document_action_api(self):
        from ai_tutor.models import StudyMaterial, DocumentChunk

        doc = StudyMaterial.objects.create(
            student=self.student,
            title='DBMS Indexing Guide',
            file_type='pdf',
            is_processed=True
        )
        DocumentChunk.objects.create(
            document=doc,
            chunk_index=1,
            page_number=1,
            content="B-Trees keep data sorted and allow searches, sequential access, insertions, and deletions in logarithmic time."
        )

        url = reverse('ai_tutor:document_action', kwargs={'document_id': doc.id})
        response = self.client.post(url, {'action': 'summary'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')
        self.assertIn('Summary', response.json()['content'])
