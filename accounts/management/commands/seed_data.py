from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import User, StudentProfile, TeacherProfile
from study_planner.models import Subject, Topic, StudyTask, StudySession, Exam
from attendance.models import AttendanceRecord
from dashboard.models import RecentActivity, AIStudyRecommendation
from notifications.models import Notification
from ai_tutor.models import (
    AIConversation, ChatMessage, SavedAnswer,
    StudyMaterial, DocumentChunk, DocumentConversation, DocumentChatMessage
)
from django.core.files.base import ContentFile

class Command(BaseCommand):
    help = 'Seeds database with realistic demo data for Student, Teacher, and Admin accounts'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding academic platform data..."))

        today = timezone.localdate()

        # 1. Create Superuser / Admin
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@apexuniversity.edu',
                'first_name': 'System',
                'last_name': 'Administrator',
                'role': User.Role.ADMIN,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        admin_user.set_password('admin123')
        admin_user.save()
        self.stdout.write(self.style.SUCCESS("✓ Admin user created: admin / admin123"))

        # 2. Create Teacher
        teacher_user, _ = User.objects.get_or_create(
            username='teacher',
            defaults={
                'email': 'prof.sharma@apexuniversity.edu',
                'first_name': 'Ramesh',
                'last_name': 'Sharma',
                'role': User.Role.TEACHER,
                'is_staff': True,
            }
        )
        teacher_user.set_password('teacher123')
        teacher_user.save()
        TeacherProfile.objects.update_or_create(
            user=teacher_user,
            defaults={
                'department': 'Computer Science & AI',
                'designation': 'Associate Professor',
                'office_location': 'Academic Block B, Suite 402'
            }
        )
        self.stdout.write(self.style.SUCCESS("✓ Teacher user created: teacher / teacher123"))

        # 3. Create Student
        student_user, _ = User.objects.get_or_create(
            username='student',
            defaults={
                'email': 'alex.patel@apexuniversity.edu',
                'first_name': 'Alex',
                'last_name': 'Patel',
                'role': User.Role.STUDENT,
                'bio': 'Passionate 3rd year CS student focusing on AI/ML and Distributed Systems.',
            }
        )
        student_user.set_password('student123')
        student_user.save()

        StudentProfile.objects.update_or_create(
            user=student_user,
            defaults={
                'student_id': 'CS2023-8842',
                'college_name': 'Apex Institute of Technology & Sciences',
                'degree': 'B.Tech in Computer Science & AI',
                'semester': 5,
                'academic_year': '2026-2027',
                'attendance_target': 75.0,
                'daily_study_target_minutes': 180,
                'preferred_language': 'en',
                'career_interest': 'AI Systems Engineer'
            }
        )
        self.stdout.write(self.style.SUCCESS("✓ Student user created: student / student123"))

        # 4. Subjects
        subjects_spec = [
            {'name': 'Data Structures & Algorithms', 'code': 'CS301', 'color': '#6366F1', 'credits': 4, 'hours': 8.0},
            {'name': 'Artificial Intelligence & ML', 'code': 'CS305', 'color': '#8B5CF6', 'credits': 4, 'hours': 7.0},
            {'name': 'Operating Systems & Concurrency', 'code': 'CS302', 'color': '#0EA5E9', 'credits': 3, 'hours': 5.0},
            {'name': 'Database Management Systems', 'code': 'CS304', 'color': '#10B981', 'credits': 3, 'hours': 5.0},
        ]
        created_subjects = []
        for s in subjects_spec:
            subj, _ = Subject.objects.update_or_create(
                student=student_user,
                name=s['name'],
                defaults={
                    'code': s['code'],
                    'color': s['color'],
                    'credits': s['credits'],
                    'target_hours_per_week': s['hours'],
                    'instructor_name': 'Dr. R. Sharma'
                }
            )
            created_subjects.append(subj)

        # 5. Study Sessions across past 7 days to seed chart and active streak
        durations = [120, 90, 150, 180, 110, 140, 160]
        for i, duration in enumerate(reversed(durations)):
            day = today - timedelta(days=i)
            subj = created_subjects[i % len(created_subjects)]
            StudySession.objects.get_or_create(
                student=student_user,
                session_date=day,
                defaults={
                    'subject': subj,
                    'duration_minutes': duration,
                    'topics_covered': f'Deep dive problem solving on {subj.name}',
                    'notes': 'Completed exercises and reviewed lecture slides.'
                }
            )

        # 6. Study Tasks
        tasks_spec = [
            {'title': 'Implement Red-Black Tree deletion in C++', 'priority': 'HIGH', 'days_ahead': 1, 'subj': created_subjects[0], 'done': False},
            {'title': 'Review Memory Paging and Virtual Memory in OS', 'priority': 'HIGH', 'days_ahead': 0, 'subj': created_subjects[2], 'done': False},
            {'title': 'Build CNN model for image classification assignment', 'priority': 'MEDIUM', 'days_ahead': 3, 'subj': created_subjects[1], 'done': False},
            {'title': 'Practice B-Tree and B+ Tree indexing queries in SQL', 'priority': 'MEDIUM', 'days_ahead': 4, 'subj': created_subjects[3], 'done': True},
            {'title': 'Revise Time Complexity Master Theorem proofs', 'priority': 'LOW', 'days_ahead': 6, 'subj': created_subjects[0], 'done': True},
        ]
        for t in tasks_spec:
            StudyTask.objects.get_or_create(
                student=student_user,
                title=t['title'],
                defaults={
                    'subject': t['subj'],
                    'priority': t['priority'],
                    'due_date': today + timedelta(days=t['days_ahead']),
                    'is_completed': t['done'],
                    'completed_at': timezone.now() if t['done'] else None
                }
            )

        # 7. Exams
        exams_spec = [
            {'title': 'Mid-Term: Artificial Intelligence & ML', 'days': 3, 'subj': created_subjects[1], 'venue': 'Auditorium Hall 2'},
            {'title': 'Theory Assessment: Operating Systems', 'days': 7, 'subj': created_subjects[2], 'venue': 'Room 105, Block A'},
            {'title': 'Practical Lab Exam: Data Structures', 'days': 12, 'subj': created_subjects[0], 'venue': 'CS Lab 3'},
        ]
        for e in exams_spec:
            Exam.objects.get_or_create(
                student=student_user,
                title=e['title'],
                defaults={
                    'subject': e['subj'],
                    'exam_date': today + timedelta(days=e['days']),
                    'venue': e['venue'],
                    'total_marks': 100.0
                }
            )

        # 8. Attendance Records
        # Create realistic attendance distribution:
        # CS301 (DSA): 18 present, 2 absent -> 90%
        # CS305 (AI/ML): 17 present, 3 absent -> 85%
        # CS302 (OS): 13 present, 7 absent -> 65% (below 75% target, trigger alerts!)
        # CS304 (DBMS): 16 present, 4 absent -> 80%
        attendance_distribution = [
            (created_subjects[0], 18, 2),
            (created_subjects[1], 17, 3),
            (created_subjects[2], 13, 7),
            (created_subjects[3], 16, 4),
        ]
        for subj, pres_count, abs_count in attendance_distribution:
            # Clean existing for idempotency
            AttendanceRecord.objects.filter(student=student_user, subject=subj).delete()
            day_offset = 1
            for _ in range(pres_count):
                AttendanceRecord.objects.create(
                    student=student_user,
                    subject=subj,
                    date=today - timedelta(days=day_offset),
                    status=AttendanceRecord.Status.PRESENT
                )
                day_offset += 1
            for _ in range(abs_count):
                AttendanceRecord.objects.create(
                    student=student_user,
                    subject=subj,
                    date=today - timedelta(days=day_offset),
                    status=AttendanceRecord.Status.ABSENT
                )
                day_offset += 1

        # 9. AI Study Recommendations
        AIStudyRecommendation.objects.filter(student=student_user).delete()
        AIStudyRecommendation.objects.create(
            student=student_user,
            title="Attendance Alert: OS & Concurrency is at 65%",
            content="Your attendance is below your 75% target. Attend the next 3 consecutive lectures to get back above the required threshold.",
            priority="HIGH",
            action_label="View Attendance Details",
            action_url="#attendance"
        )
        AIStudyRecommendation.objects.create(
            student=student_user,
            title="Prepare for Mid-Term: AI & ML in 3 Days",
            content="Based on your syllabus, you haven't reviewed Backpropagation & Neural Net optimization. Let's do a 45-minute revision session.",
            priority="HIGH",
            action_label="Start AI Revision",
            action_url="#ai-tutor"
        )
        AIStudyRecommendation.objects.create(
            student=student_user,
            title="Great 7-Day Study Streak! 🔥",
            content="You've maintained consistent focus every day this week. Review your DSA tree algorithms before tonight's target deadline.",
            priority="MEDIUM",
            action_label="Review DSA Tasks",
            action_url="#planner"
        )

        # 10. Recent Activities
        RecentActivity.objects.filter(user=student_user).delete()
        RecentActivity.objects.create(user=student_user, title="Completed 2h 30m study session on AI/ML", category="STUDY", icon="book-open")
        RecentActivity.objects.create(user=student_user, title="Checked off task: B-Tree Indexing in SQL", category="TASK", icon="check-circle-2")
        RecentActivity.objects.create(user=student_user, title="Logged attendance for Operating Systems", category="ATTENDANCE", icon="user-check")
        RecentActivity.objects.create(user=student_user, title="Generated study plan for Mid-Term Exams", category="PLANNER", icon="calendar")

        # 11. In-App Notifications
        Notification.objects.filter(user=student_user).delete()
        Notification.objects.create(
            user=student_user,
            title="Upcoming Exam: AI & ML in 3 Days",
            message="Your Mid-Term Examination for CS305 starts at 10:00 AM on auditorium Hall 2.",
            notification_type=Notification.Type.EXAM,
            is_read=False
        )
        Notification.objects.create(
            user=student_user,
            title="Attendance Warning: Operating Systems",
            message="Your current attendance is 65%, which is below the mandatory 75% threshold.",
            notification_type=Notification.Type.ATTENDANCE,
            is_read=False
        )
        Notification.objects.create(
            user=student_user,
            title="New Assignment: Red-Black Trees",
            message="Prof. Sharma posted the C++ implementation assignment due in 4 days.",
            notification_type=Notification.Type.TASK,
            is_read=True
        )

        # 12. Seed Demo AI Conversation & Saved Answer
        AIConversation.objects.filter(student=student_user).delete()
        sample_conv = AIConversation.objects.create(
            student=student_user,
            subject=created_subjects[0],
            title="Dijkstra Shortest Path & Complexity",
            mode=AIConversation.Mode.TUTOR,
            language=AIConversation.Language.ENGLISH
        )
        ChatMessage.objects.create(
            conversation=sample_conv,
            role=ChatMessage.Role.USER,
            content="Can you explain Dijkstra's algorithm step-by-step with min-heap complexity?"
        )
        sample_ai_msg = ChatMessage.objects.create(
            conversation=sample_conv,
            role=ChatMessage.Role.ASSISTANT,
            content=(
                "### 💡 Dijkstra's Shortest Path Algorithm\n\n"
                "#### 📌 Core Intuition\n"
                "Dijkstra's Algorithm finds the shortest path from a starting source node to all other vertices in a weighted graph containing **non-negative edge weights**.\n\n"
                "#### 🔍 Step-by-Step Breakdown\n"
                "1. **Initialization:** Set `dist[source] = 0` and `dist[v] = infinity` for all other vertices. Push `(0, source)` into a Min-Priority Queue.\n"
                "2. **Greedy Selection:** In each step, extract vertex $u$ with the minimum distance.\n"
                "3. **Edge Relaxation:** For every neighbor $v$ of $u$ with weight $w$, if `dist[u] + w < dist[v]`, update `dist[v]` and push `(dist[v], v)` into the queue.\n"
                "4. **Termination:** Continue until priority queue is empty.\n\n"
                "#### 💻 Python Implementation (Min-Heap)\n"
                "```python\n"
                "import heapq\n\n"
                "def dijkstra(graph, start):\n"
                "    distances = {node: float('inf') for node in graph}\n"
                "    distances[start] = 0\n"
                "    pq = [(0, start)]  # (distance, node)\n\n"
                "    while pq:\n"
                "        curr_d, u = heapq.heappop(pq)\n"
                "        if curr_d > distances[u]:\n"
                "            continue\n\n"
                "        for v, weight in graph[u]:\n"
                "            if curr_d + weight < distances[v]:\n"
                "                distances[v] = curr_d + weight\n"
                "                heapq.heappush(pq, (distances[v], v))\n\n"
                "    return distances\n"
                "```\n\n"
                "#### ⚡ Asymptotic Complexity\n"
                "- **Time Complexity:** $O((V + E) \\log V)$ using a binary min-heap priority queue.\n"
                "- **Space Complexity:** $O(V)$ for storing distance map and min-heap."
            ),
            is_saved=True
        )
        SavedAnswer.objects.create(
            student=student_user,
            message=sample_ai_msg,
            subject=created_subjects[0],
            title="Dijkstra Shortest Path & Complexity"
        )

        # 13. Seed Demo Study Material for RAG Document Chat
        StudyMaterial.objects.filter(student=student_user).delete()
        demo_content = (
            "CHAPTER 1: PROCESS CONCURRENCY AND MUTEX LOCKS\n"
            "Concurrency occurs when multiple instruction sequences execute simultaneously.\n"
            "A critical section is a piece of code that accesses shared resources. If two processes\n"
            "access the critical section concurrently without mutual exclusion, a race condition occurs.\n"
            "Peterson's algorithm and hardware atomic operations such as Test-And-Set provide mutual exclusion.\n\n"
            "CHAPTER 2: VIRTUAL MEMORY AND DEMAND PAGING\n"
            "Virtual memory decouples user logical memory from physical memory. Demand paging loads pages\n"
            "only when they are required during process execution. When a process attempts to access a page\n"
            "whose valid bit is 0, the Memory Management Unit (MMU) generates a hardware trap called a page fault.\n"
            "The operating system fetches the required page from disk swap space into an available physical frame\n"
            "and updates the Page Table Entry (PTE). The Effective Access Time (EAT) is computed as:\n"
            "EAT = (1 - p) * Memory_Access_Time + p * Page_Fault_Service_Time\n\n"
            "CHAPTER 3: PAGE REPLACEMENT ALGORITHMS\n"
            "When physical memory frames are full, the OS replaces an existing page. Standard algorithms include:\n"
            "1. First-In-First-Out (FIFO): Simple to implement, but suffers from Belady's Anomaly.\n"
            "2. Optimal Page Replacement (OPT): Replaces page that will not be used for longest period of time.\n"
            "3. Least Recently Used (LRU): Replaces page that has not been used for the longest period of time."
        )

        demo_doc = StudyMaterial.objects.create(
            student=student_user,
            subject=created_subjects[2],  # OS
            title="OS Module 4: Concurrency & Virtual Memory",
            file_type=StudyMaterial.FileType.PDF,
            page_count=3,
            file_size_bytes=len(demo_content.encode('utf-8')),
            is_processed=True
        )
        demo_doc.file.save("os_concurrency_virtual_memory.txt", ContentFile(demo_content.encode('utf-8')), save=True)

        chunks_specs = [
            (1, 1, "Concurrency occurs when multiple instruction sequences execute simultaneously. A critical section is a piece of code that accesses shared resources. If two processes access the critical section concurrently without mutual exclusion, a race condition occurs. Peterson's algorithm and hardware atomic operations such as Test-And-Set provide mutual exclusion."),
            (2, 2, "Virtual memory decouples user logical memory from physical memory. Demand paging loads pages only when they are required during process execution. When a process attempts to access a page whose valid bit is 0, the Memory Management Unit (MMU) generates a hardware trap called a page fault."),
            (3, 2, "The operating system fetches the required page from disk swap space into an available physical frame and updates the Page Table Entry (PTE). The Effective Access Time (EAT) is computed as: EAT = (1 - p) * Memory_Access_Time + p * Page_Fault_Service_Time."),
            (4, 3, "When physical memory frames are full, the OS replaces an existing page. Standard algorithms include: 1. FIFO (suffers from Belady's Anomaly), 2. OPT (theoretical benchmark), 3. LRU (replaces page unused for longest time using hardware timestamps or stack)."),
        ]
        for c_idx, p_num, c_text in chunks_specs:
            DocumentChunk.objects.create(
                document=demo_doc,
                chunk_index=c_idx,
                page_number=p_num,
                content=c_text
            )

        # Seed Document Conversation & QA
        doc_conv = DocumentConversation.objects.create(
            student=student_user,
            document=demo_doc,
            title="Chat: Concurrency & Paging"
        )
        DocumentChatMessage.objects.create(
            conversation=doc_conv,
            role=DocumentChatMessage.Role.USER,
            content="What happens during a page fault and how is EAT calculated?"
        )
        DocumentChatMessage.objects.create(
            conversation=doc_conv,
            role=DocumentChatMessage.Role.ASSISTANT,
            content=(
                "### 🔍 Page Fault Handling & EAT Formula\n\n"
                "According to your uploaded notes, here is the exact breakdown:\n\n"
                "#### 1. Page Fault Sequence **[Page 2]**\n"
                "- When a process attempts to access an address whose valid-invalid bit in the page table is marked `0` (invalid), the MMU issues a hardware trap to the OS known as a **Page Fault**.\n"
                "- The OS pauses the process, locates the desired page on backing store (disk swap), finds a free physical frame in RAM, and transfers the page into memory.\n"
                "- The Page Table Entry (PTE) is updated with the new frame number and valid bit set to `1`, after which the trapped instruction restarts.\n\n"
                "#### 2. Effective Access Time (EAT) Calculation **[Page 2]**\n"
                "The formula given in the document is:\n"
                "$$\\text{EAT} = (1 - p) \\times \\text{Memory\\_Access\\_Time} + p \\times \\text{Page\\_Fault\\_Service\\_Time}$$\n"
                "Where $p$ represents the page fault rate ($0 \\le p \\le 1$)."
            ),
            page_citations=[
                {'page_number': 2, 'excerpt': 'When a process attempts to access a page whose valid bit is 0, the MMU generates a hardware trap called a page fault...'}
            ]
        )

        self.stdout.write(self.style.SUCCESS("✓ All demo data, subjects, tasks, attendance records & AI recommendations successfully populated!"))
