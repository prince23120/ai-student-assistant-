# 🎓 AI Student Assistant – Enterprise Learning Platform

A full-stack, AI-powered academic operating system built with **Django 6**, **Python 3.13**, **Tailwind CSS**, and modern software design principles.

---

## 🌟 Implemented in Phase 1

### 1. Foundation & Custom Architecture
- **Normalized Multi-Role Authentication System**:
  - Custom `User` model (`AbstractUser`) supporting `STUDENT`, `TEACHER`, and `ADMIN` roles.
  - One-to-One linked `StudentProfile` and `TeacherProfile` with automatic signal creation.
  - Role-based authorization decorators (`@student_required`, `@teacher_required`, `@admin_required`).
  - Session management with "Remember Me" toggle.
  - Full registration, login, logout, profile update with avatar uploads, and password change.

### 2. Relational Academic Database Models
- `Subject`: Course code, credits, target study hours/week, instructor name, custom color tags.
- `StudyTask`: Task prioritization (Low, Medium, High), due dates, completion timestamps.
- `StudySession`: Timestamped study logging in minutes, topics covered, session notes.
- `Exam`: Upcoming examinations with syllabus, venue, date, time, marks.
- `AttendanceRecord`: Present, Absent, Cancelled status tracking per subject.
- `AIStudyRecommendation`: Priority-based actionable recommendations for students.
- `RecentActivity`: Real-time audit timeline of academic actions.
- `Notification`: In-app notification center with unread counters.

### 3. Modern SaaS Student Dashboard
- **Glassmorphism & Clean Typography**: Tailwind CSS + Inter & Plus Jakarta Sans typography.
- **Dynamic Dark & Light Mode**: System auto-detection with local storage persistence.
- **4 Key Academic KPI Cards**:
  - Total study hours (all-time and current week breakdown)
  - Study Streak calculation (consecutive active days)
  - Task completion progress bar
  - Attendance gauge with threshold alerts and minimum classes required calculator
- **Interactive Chart.js Visualizer**: 7-day study velocity chart with gradient fill.
- **Today's Focus & Live Task Toggle**: Real-time AJAX completion status update without page reload.
- **AI Recommendation Engine**: Dismissible AI alert cards with action links.
- **Quick Study Logging Modal**: Instant session logging directly from the dashboard.
- **Upcoming Exams Timeline**: Days-left countdown badge.
- **Subject Attendance Ledger**: Color-coded progress bars highlighting low-attendance subjects.

---

## 🚀 Quick Start Guide

### 1. Activate Virtual Environment
```bash
source venv/bin/activate
```

### 2. Apply Database Migrations
```bash
python manage.py migrate
```

### 3. Populate Demo Data (Subjects, Tasks, Attendance, Sessions)
```bash
python manage.py seed_data
```

### 4. Run the Development Server
```bash
python manage.py runserver 8000
```
Open your browser at: **`http://127.0.0.1:8000/`**

---

## 🔑 Pre-Seeded Accounts for Testing

| Role | Username | Password | Email |
| :--- | :--- | :--- | :--- |
| **Student** | `student` | `student123` | `alex.patel@apexuniversity.edu` |
| **Teacher** | `teacher` | `teacher123` | `prof.sharma@apexuniversity.edu` |
| **Administrator** | `admin` | `admin123` | `admin@apexuniversity.edu` |

*(You can also click "Create student account" on `/accounts/register/` to test new registrations).*

---

## 🗺️ 12-Phase Roadmap

- [x] **Phase 1**: Project inspection, authentication, relational database schema, and modern Student/Admin dashboard.
- [x] **Phase 2**: AI Study Tutor Chatbot (Gemini/OpenAI, Hindi/English/Hinglish, step-by-step explanations, code debugging, exam answers, saved answers).
- [x] **Phase 3**: AI Chat with PDF / RAG (Multi-format parser for PDF, DOCX, PPTX, TXT; BM25 vector chunking; RAG Q&A with clickable page citations; automated Summaries, Notes, MCQs).
- [ ] **Phase 4**: AI Notes Generator & Flashcard System (Subject/Semester organization, export).
- [ ] **Phase 5**: AI Quiz & Examination System (MCQ, True/False, Fill-in-the-blank, timed evaluations).
- [ ] **Phase 6**: Smart Study Planner & Automated Timetable Scheduler.
- [ ] **Phase 7**: Academic Analytics Dashboard (Chart.js deep dive, weakness diagnosis).
- [ ] **Phase 8**: Assignment Assistant & Attendance Manager (Target simulations, deadline tracker).
- [ ] **Phase 9**: AI Career Assistant (Resume analyzer, ATS optimizer, interview prep).
- [ ] **Phase 10**: Teacher & Administrator Portals (Class rosters, announcements, AI usage monitoring).
- [ ] **Phase 11**: Real-Time Notification Center & Audio Integration (Speech-to-text / TTS).
- [ ] **Phase 12**: Security Audit, Production Optimization & Deployment.
