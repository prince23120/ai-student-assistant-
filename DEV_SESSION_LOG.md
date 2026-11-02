# 📝 AI Student Assistant — Session & Architecture Log

This file contains the complete record of the conversation, decisions, technical architecture, and progress made during our development sessions in the Antigravity IDE.

---

## 📌 Conversation & Development Timeline

### Session 1: Project Initialization & Inspection
- **Workspace State**: Inspected directory `/Users/princebansal/Desktop/ai student assistant`. Found an empty workspace with Python 3.13.2.
- **Environment Setup**: Created a clean virtual environment (`venv`) and installed core dependencies:
  - `Django 6.1.2`
  - `djangorestframework 3.18.3`
  - `python-dotenv 1.2.4`
  - `Pillow 13.0.0`
- **Application Structure**: Structured modular Django apps:
  - `accounts/`, `dashboard/`, `study_planner/`, `attendance/`, `notifications/`, `ai_tutor/`, `notes/`, `quizzes/`, `assignments/`, `analytics/`, `career/`, `campus/`.

---

### Session 2: Phase 1 — Foundation, Multi-Role Auth & Student Dashboard
- **Custom User Model**: Built `accounts.models.User` inheriting `AbstractUser` with roles:
  - `STUDENT`, `TEACHER`, `ADMIN`
  - Linked `StudentProfile` and `TeacherProfile` automatically created via `post_save` signals.
- **Role Decorators**: `@student_required`, `@teacher_required`, `@admin_required`.
- **Relational Models**:
  - `Subject`, `Topic`, `StudyTask`, `StudySession`, `Exam` (`study_planner/models.py`)
  - `AttendanceRecord` with percentage calculation & classes-needed recovery formula (`attendance/models.py`)
  - `Notification` with category tags & unread counts (`notifications/models.py`)
  - `RecentActivity` timeline & `AIStudyRecommendation` actionable alert cards (`dashboard/models.py`)
- **Modern SaaS UI**:
  - Tailwind CSS + Inter & Plus Jakarta Sans typography.
  - Dark/Light mode toggle with local storage persistence.
  - Responsive collapsible sidebar with live route badges.
  - Interactive Chart.js 7-Day Study Velocity line chart with gradient fill.
  - Today's tasks with instant AJAX completion toggling without page reload.
  - Quick Study Session logging modal.
- **Automated Seeder Command**: `python manage.py seed_data` populating:
  - Admin: `admin` / `admin123`
  - Teacher: `teacher` / `teacher123`
  - Student: `student` / `student123`
  - 4 University Subjects (DSA, OS, AI/ML, DBMS), 7 days of study sessions, attendance records, tasks, exams, and notifications.

---

### Session 3: Phase 2 — AI Study Tutor Chatbot
- **Tutor Data Models**:
  - `AIConversation`: Tracks conversation title, mode, language, and subject.
  - `ChatMessage`: Stores role (user/assistant) and markdown content.
  - `SavedAnswer`: Bookmarking system for high-yield exam answers and code explanations.
- **Pedagogical Modes**:
  - `TUTOR`: Intuitive analogy, step-by-step breakdown, key takeaways.
  - `CODE_DEBUG`: Line-by-line diagnosis, syntax-highlighted code, Big-O time and space complexity ($O((V+E)\log V)$, $O(n\log n)$).
  - `EXAM_5_MARKS`: Crisp 200–250 word university exam answer format with diagrams.
  - `EXAM_10_MARKS`: In-depth 450–600 word comprehensive answer with theory, architecture, proofs, and applications.
  - `SIMPLIFY`: ELI5 explanations with everyday metaphors.
- **Languages**: English, Hindi (हिंदी), and conversational Hinglish (widely spoken in Indian universities).
- **AI Services**:
  - Direct REST integration with Google Gemini (`GEMINI_API_KEY`) and OpenAI (`OPENAI_API_KEY`).
  - Intelligent built-in academic fallback engine ensuring zero downtime when offline.
- **Frontend Workspace**:
  - `marked.js` markdown rendering.
  - `highlight.js` syntax highlighting with dark theme.
  - Interactive prompt chips for immediate testing.
  - Copy to clipboard with visual "Copied!" feedback.
  - Save/Bookmark to dedicated `/tutor/saved/` repository.
- **UI Bug Fix**: Resolved Unicode string escaping (`\u000A`, `\u0027`) by replacing attribute escaping with a clean `<textarea class="raw-markdown hidden">` container.

---

### Session 4: Phase 3 — AI Chat with PDF & Documents (RAG)
- **Multi-Format Ingestion**:
  - Built `ai_tutor/document_parser.py` supporting:
    - PDF documents (PyMuPDF `fitz` with flate stream inspection fallback)
    - Microsoft Word (`.docx` via XML element tree parsing)
    - PowerPoint slides (`.pptx` parsed slide-by-slide)
    - Plain text & Markdown (`.txt`, `.md`)
  - Sliding-window chunker: 700-character segments with 100-character overlap with page attribution.
- **RAG Engine (`ai_tutor/rag_engine.py`)**:
  - BM25 / TF-IDF rank retrieval matching student questions to top relevant chunks.
  - Context-enriched prompt generation requiring the AI to cite exact page numbers `[Page X]` and `[Slide Y]`.
  - Clickable page citation pills attached to responses displaying the source excerpt.
  - Automated study tools: Executive Summary, High-Yield Revision Notes, Practice MCQs.
- **Document Workspace**:
  - Document Library at `/tutor/documents/` with file upload modal (up to 25MB).
  - Split-pane chat interface at `/tutor/documents/<id>/`.
- **RAG Grounding Update**: Enhanced the fallback engine to extract actual text sentences and arguments from uploaded documents (such as legal/social science papers) rather than defaulting to generic CS code templates.

---

## 🧪 Automated Testing Verification

All 18 unit and integration tests passing:
- `test_user_roles`: Verified Student, Teacher, Admin roles.
- `test_student_profile_created`: Verified signal creation of profiles.
- `test_login_flow` & `test_login_with_email`: Verified dual-identifier authentication.
- `test_registration_flow`: Verified user & profile creation with degree & semester.
- `test_streak_calculation`: Verified active day streak algorithm.
- `test_attendance_calculation`: Verified percentage & threshold status.
- `test_student_dashboard_authenticated`: Verified full KPI render.
- `test_task_toggle_ajax`: Verified task checkoff without reload.
- `test_recommendation_dismiss_ajax`: Verified AI card dismissal.
- `test_workspace_view`: Verified AI Tutor interface.
- `test_create_conversation`: Verified multi-mode conversation creation.
- `test_send_message_api`: Verified full AJAX question/answer exchange.
- `test_toggle_save_message_and_view`: Verified bookmarking & saved answers.
- `test_delete_conversation`: Verified cascading deletion.
- `test_document_upload_and_chunking`: Verified multi-format document parser.
- `test_document_rag_chat_api`: Verified BM25 chunk retrieval & page citations.
- `test_document_action_api`: Verified automated summary & MCQ generation.

```bash
$ ./venv/bin/python manage.py test
Ran 18 tests in 5.575s
OK
```

---

## 🚀 Running the Project

To run the platform at any time:
```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Run server
python manage.py runserver 8000
```
Open browser at: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

### Pre-Seeded Logins:
- **Student**: `student` / `student123`
- **Teacher**: `teacher` / `teacher123`
- **Administrator**: `admin` / `admin123`
