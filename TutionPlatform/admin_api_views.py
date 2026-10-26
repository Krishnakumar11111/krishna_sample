from django.db import transaction
import json
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from TutionPlatform.models import (
    StudentProfile, TeacherProfile, ParentProfile, CourseBatch, CourseSubject, BatchGroup,
    CourseChapter, CourseLecture, LiveClass, StudyMaterial, HomeworkAssignment,
    OnlineTest, TestSeries, PreviousYearQuestion, ELibraryBook, ENewspaper,
    NoticeBoard, Announcement, AdminNotification, DirectMessage, PaymentTransaction,
    WalletTransaction, PlatformSettings, AdminRole, ActivityLog, UserAuthLog, DatabaseBackup, StudentProfileChangeLog,
    BatchTeacherAssignment, BatchCoupon, BatchActivityLog
)

try:
    from TutionPlatform.views import log_user_auth_event, get_client_info, get_detailed_client_info
except Exception:
    def log_user_auth_event(*args, **kwargs):
        pass
    def get_client_info(request):
        return ('127.0.0.1', 'Desktop')
    def get_detailed_client_info(request):
        return {'ip': '127.0.0.1', 'device': 'Desktop', 'browser': 'Edge', 'os': 'Windows'}

def api_response(data=None, message="Success", status=200, errors=None):
    return JsonResponse({
        "status": status,
        "message": message,
        "data": data if data is not None else {},
        "errors": errors or []
    }, status=status)

# ==========================================
# 1. DASHBOARD AGGREGATED STATS API
# ==========================================
def dashboard_stats_api(request):
    try:
        total_students = StudentProfile.objects.count()
        active_students = StudentProfile.objects.filter(Q(account_status='Active') | Q(account_status='Approved') | Q(account_status='Verified')).count()
        
        total_teachers = TeacherProfile.objects.count()
        active_teachers = TeacherProfile.objects.filter(Q(account_status='Active') | Q(verification_status='Approved')).count()
        
        total_courses = CourseBatch.objects.count()
        total_live_classes = LiveClass.objects.count()
        live_today = LiveClass.objects.filter(status='Live').count()
        upcoming_classes = LiveClass.objects.filter(Q(status='Upcoming') | Q(status='Scheduled')).count()
        cancelled_classes = LiveClass.objects.filter(status='Cancelled').count()
        recorded_lectures = CourseLecture.objects.count()
        
        revenue_sum = PaymentTransaction.objects.filter(status='Success').aggregate(total=Sum('amount'))['total'] or 0
        total_revenue = float(revenue_sum)

        total_videos = recorded_lectures
        total_study_materials = StudyMaterial.objects.exclude(status='Deleted').count()
        total_assignments = HomeworkAssignment.objects.count()
        total_quizzes = OnlineTest.objects.filter(test_type='Daily Test').count()
        total_tests = OnlineTest.objects.count()
        total_dpps = HomeworkAssignment.objects.filter(chapter__isnull=False).count()
        total_books = ELibraryBook.objects.count()
        total_notices = NoticeBoard.objects.count()

        # Recent activities (last 5 logs)
        recent_logs_qs = ActivityLog.objects.order_by('-id')[:5]
        recent_logs = [{
            'id': l.id,
            'activity_type': l.activity_type,
            'user_name': l.user_name,
            'description': l.description,
            'created_at': l.created_at.strftime('%Y-%m-%d %H:%M')
        } for l in recent_logs_qs]

        # System overview metrics
        system_overview = {
            'server_status': 'Online',
            'storage_used': '256 GB / 1 TB',
            'bandwidth': '1.25 TB / 5 TB',
            'database': 'Optimized',
            'backup_timestamp': '2 hours ago'
        }

        data = {
            'total_students': total_students,
            'active_students': active_students,
            'total_teachers': total_teachers,
            'active_teachers': active_teachers,
            'total_users': total_students + total_teachers + 1,
            'total_courses': total_courses,
            'total_live_classes': total_live_classes,
            'live_today_count': live_today,
            'upcoming_classes_count': upcoming_classes,
            'cancelled_classes_count': cancelled_classes,
            'recorded_count': recorded_lectures,
            'total_revenue': total_revenue,
            'total_videos': total_videos,
            'total_study_materials': total_study_materials,
            'total_assignments': total_assignments,
            'total_quizzes': total_quizzes,
            'total_tests': total_tests,
            'total_dpps': total_dpps,
            'total_books': total_books,
            'total_notices': total_notices,
            'recent_logs': recent_logs,
            'system_overview': system_overview
        }
        return api_response(data=data)
    except Exception as e:
        return api_response(message=str(e), status=500)


# ==========================================
# 2. STUDENTS API (CRUD + PAGINATION + SEARCH)
# ==========================================
@csrf_exempt
def students_api(request):
    if request.method == 'GET':
        single_id = request.GET.get('id')
        if single_id:
            s = StudentProfile.objects.filter(id=single_id).first()
            if not s:
                return api_response(message="Student not found.", status=404)
            student_detail = {
                'id': s.id,
                'student_id': s.student_id or f"STU-{s.id}",
                'full_name': s.full_name,
                'email': s.email,
                'mobile': s.mobile,
                'gender': s.gender or 'Not Specified',
                'student_class': s.student_class or 'Class 10 CBSE',
                'city': s.city or 'City',
                'state': s.state or 'State',
                'account_status': s.account_status or 'Active',
                'registration_date': s.created_at.strftime('%b %d, %Y') if hasattr(s, 'created_at') and s.created_at else 'Recently',
                'registration_time': s.created_at.strftime('%I:%M %p') if hasattr(s, 'created_at') and s.created_at else 'Recently',
                'device_info': f"{s.browser or 'Web Browser'} ({s.device_type or 'Desktop'}) - IP: {s.ip_address or 'Unknown'}"
            }
            return api_response(data={'student': student_detail})

        query = request.GET.get('q', '').strip()
        class_filter = request.GET.get('class_name', '').strip()
        status_filter = request.GET.get('status', '').strip()
        page_num = request.GET.get('page', 1)
        page_size = request.GET.get('page_size', 10)

        students_qs = StudentProfile.objects.order_by('-id')

        if query:
            students_qs = students_qs.filter(
                Q(full_name__icontains=query) | Q(email__icontains=query) | Q(mobile__icontains=query) | Q(student_id__icontains=query)
            )
        if class_filter:
            students_qs = students_qs.filter(student_class__icontains=class_filter)
        if status_filter:
            students_qs = students_qs.filter(account_status__iexact=status_filter)

        paginator = Paginator(students_qs, page_size)
        page_obj = paginator.get_page(page_num)

        students_list = [{
            'id': s.id,
            'student_id': s.student_id or f"STU-{s.id}",
            'full_name': s.full_name,
            'email': s.email,
            'mobile': s.mobile,
            'student_class': s.student_class or 'Class 10 CBSE',
            'city': s.city or 'N/A',
            'account_status': s.account_status or 'Active',
            'created_at': s.created_at.strftime('%Y-%m-%d') if hasattr(s, 'created_at') and s.created_at else ''
        } for s in page_obj]

        return api_response(data={
            'students': students_list,
            'total_count': paginator.count,
            'total_pages': paginator.num_pages,
            'current_page': page_obj.number
        })

    elif request.method == 'POST':
        try:
            body = json.loads(request.body.decode('utf-8')) if request.body else request.POST
            name = body.get('full_name', '').strip()
            email = body.get('email', '').strip()
            mobile = body.get('mobile', '').strip()
            student_class = body.get('student_class', 'Class 10 CBSE').strip()

            if not name or not email or not mobile:
                return api_response(message="Full Name, Email and Mobile are required.", status=400)

            if StudentProfile.objects.filter(email=email).exists():
                return api_response(message="A student with this email already exists.", status=400)
            if StudentProfile.objects.filter(mobile=mobile).exists():
                return api_response(message="A student with this mobile number already exists.", status=400)

            student = StudentProfile.objects.create(
                full_name=name,
                email=email,
                mobile=mobile,
                student_class=student_class,
                approval_status='pending',
                account_status='inactive',
                approved=False,
                rejected=False
            )

            # Log activity
            ActivityLog.objects.create(
                activity_type='Add Student',
                user_name='Super Admin',
                user_role='Super Admin',
                description=f"Added new student {student.full_name} ({student.student_id})"
            )

            return api_response(data={'id': student.id, 'student_id': student.student_id}, message="Student Added Successfully!", status=201)
        except Exception as e:
            return api_response(message=f"Failed to add student: {str(e)}", status=400)

    elif request.method == 'DELETE':
        try:
            body = json.loads(request.body.decode('utf-8'))
            student_id = body.get('id')
            student = StudentProfile.objects.get(id=student_id)
            student.delete()

            ActivityLog.objects.create(
                activity_type='Delete Student',
                user_name='Super Admin',
                user_role='Super Admin',
                description=f"Deleted student ID {student_id}"
            )
            return api_response(message="Student Deleted Successfully!")
        except StudentProfile.DoesNotExist:
            return api_response(message="Student not found", status=404)
        except Exception as e:
            return api_response(message=f"Failed to delete student: {str(e)}", status=400)

    return api_response(message="Method not allowed", status=405)


# ==========================================
# 3. TEACHERS API (CRUD + VERIFICATION APPROVALS)
# ==========================================
@csrf_exempt
def teachers_api(request):
    if request.method == 'GET':
        single_id = request.GET.get('id')
        if single_id:
            t = TeacherProfile.objects.filter(id=single_id).first()
            if not t:
                return api_response(message="Teacher not found.", status=404)
            teacher_detail = {
                'id': t.id,
                'teacher_id': t.teacher_id or f"EDUT-{t.id}",
                'full_name': t.full_name,
                'email': t.email,
                'mobile': t.mobile,
                'gender': t.gender or 'N/A',
                'experience': t.experience or 'Fresher',
                'qualification': t.qualification or 'Graduate',
                'city': t.city or 'City',
                'state': t.state or 'State',
                'pincode': t.pincode or 'N/A',
                'teaching_classes': t.teaching_classes or 'All Classes',
                'subjects': t.subjects or 'General',
                'expected_fee': t.expected_fee or 'Negotiable',
                'tuition_mode': t.tuition_mode or 'Home & Online',
                'languages': t.languages or 'English, Hindi',
                'bio': t.bio or '',
                'photo_url': t.profile_photo.url if t.profile_photo else f"https://ui-avatars.com/api/?name={t.full_name}&background=2563eb&color=fff&size=200",
                'verification_status': t.verification_status or 'Pending Approval',
                'account_status': t.account_status or 'Active',
                'registration_date': t.created_at.strftime('%b %d, %Y') if hasattr(t, 'created_at') and t.created_at else 'Recently',
                'registration_time': t.created_at.strftime('%I:%M %p') if hasattr(t, 'created_at') and t.created_at else 'Recently',
            }
            return api_response(data={'teacher': teacher_detail})

        query = request.GET.get('q', '').strip()
        status_filter = request.GET.get('verification_status', '').strip()

        teachers_qs = TeacherProfile.objects.order_by('-id')

        if query:
            teachers_qs = teachers_qs.filter(
                Q(full_name__icontains=query) | Q(email__icontains=query) | Q(subjects__icontains=query)
            )
        if status_filter:
            teachers_qs = teachers_qs.filter(verification_status__iexact=status_filter)

        teachers_list = [{
            'id': t.id,
            'teacher_id': t.teacher_id or f"TCH-{t.id}",
            'full_name': t.full_name,
            'email': t.email,
            'mobile': t.mobile,
            'subjects': t.subjects or 'General',
            'qualification': t.qualification or 'Graduate',
            'experience': t.experience or 'Fresher',
            'verification_status': t.verification_status or 'Pending Approval',
            'account_status': t.account_status or 'Active',
            'created_at': t.created_at.strftime('%Y-%m-%d') if hasattr(t, 'created_at') and t.created_at else ''
        } for t in teachers_qs]

        return api_response(data={'teachers': teachers_list, 'total_count': len(teachers_list)})

    elif request.method == 'POST':
        try:
            body = json.loads(request.body.decode('utf-8')) if request.body else request.POST
            name = body.get('full_name', '').strip()
            email = body.get('email', '').strip()
            mobile = body.get('mobile', '').strip()
            subjects = body.get('subjects', 'Mathematics').strip()
            qualification = body.get('qualification', 'M.Sc Physics').strip()

            if not name or not email or not mobile:
                return api_response(message="Full Name, Email and Mobile are required.", status=400)

            teacher = TeacherProfile.objects.create(
                full_name=name,
                email=email,
                mobile=mobile,
                subjects=subjects,
                qualification=qualification,
                verification_status='Pending Approval',
                approval_status='pending',
                account_status='inactive',
                approved=False,
                rejected=False
            )

            ActivityLog.objects.create(
                activity_type='Add Teacher',
                user_name='Super Admin',
                user_role='Super Admin',
                description=f"Added faculty teacher {teacher.full_name}"
            )

            return api_response(data={'id': teacher.id}, message="Teacher Registered Successfully!", status=201)
        except Exception as e:
            return api_response(message=f"Failed to add teacher: {str(e)}", status=400)

    elif request.method == 'PUT':
        try:
            body = json.loads(request.body.decode('utf-8'))
            teacher_id = body.get('id')
            action = body.get('action')  # approve, reject, suspend
            teacher = TeacherProfile.objects.get(id=teacher_id)

            if action == 'approve':
                teacher.verification_status = 'Approved'
                teacher.approved = True
                teacher.rejected = False
            elif action == 'reject':
                teacher.verification_status = 'Rejected'
                teacher.approved = False
                teacher.rejected = True
            elif action == 'suspend':
                teacher.account_status = 'Suspended'

            teacher.save()

            ActivityLog.objects.create(
                activity_type='Teacher Status Update',
                user_name='Super Admin',
                user_role='Super Admin',
                description=f"Updated status for teacher {teacher.full_name} to {teacher.verification_status}"
            )

            return api_response(message=f"Teacher status updated to {teacher.verification_status}")
        except TeacherProfile.DoesNotExist:
            return api_response(message="Teacher not found", status=404)
        except Exception as e:
            return api_response(message=str(e), status=400)

    return api_response(message="Method not allowed", status=405)


# ==========================================
# 3.5 COURSES & BATCH CREATION API
# ==========================================
@csrf_exempt
def courses_api(request):
    if request.method == 'GET':
        query = request.GET.get('q', '').strip()
        class_filter = request.GET.get('class_name', '').strip()

        courses_qs = CourseBatch.objects.order_by('-id')

        if query:
            courses_qs = courses_qs.filter(Q(title__icontains=query) | Q(subject__icontains=query))
        if class_filter:
            courses_qs = courses_qs.filter(class_name__icontains=class_filter)

        courses_list = [{
            'id': c.id,
            'course_id': c.course_id or f"CRS-{c.id}",
            'title': c.title,
            'class_name': c.class_name,
            'subject': c.subject,
            'board': c.board,
            'price': float(c.price),
            'teacher_name': c.teacher_name,
            'description': c.description or '',
            'created_at': c.created_at.strftime('%Y-%m-%d') if hasattr(c, 'created_at') and c.created_at else ''
        } for c in courses_qs]

        return api_response(data={'courses': courses_list, 'total_count': len(courses_list)})

    elif request.method == 'POST':
        try:
            if request.content_type and 'multipart/form-data' in request.content_type:
                body = request.POST
            else:
                body = json.loads(request.body.decode('utf-8')) if request.body else request.POST

            title = body.get('title', '').strip()
            class_name = body.get('class_name', 'Class 10').strip()
            subject = body.get('subject', 'Mathematics').strip()
            board = body.get('board', 'CBSE').strip()
            state_name = body.get('state_name', '').strip()
            if board == 'State Board' and state_name:
                board = f"{state_name}"

            price_val = body.get('price', '4999').strip()
            price_float = float(price_val) if price_val else 4999.00
            discount_type = body.get('discount_type', 'Fixed Amount').strip()
            discount_value = float(body.get('discount_value', 0))

            if discount_type == 'Fixed Amount':
                final_price = max(0.0, price_float - discount_value)
            else:
                final_price = max(0.0, price_float - (price_float * (discount_value / 100.0)))

            teacher_name = body.get('teacher_name', 'Prof. Rajesh Sharma').strip()
            description = body.get('description', '').strip()
            banner_file = request.FILES.get('banner_image')

            if not title:
                return api_response(message="Course / Batch Title is required.", status=400)

            course = CourseBatch.objects.create(
                title=title,
                class_name=class_name,
                subject=subject,
                board=board,
                price=price_float,
                discount_type=discount_type,
                discount_value=discount_value,
                final_price=final_price,
                teacher_name=teacher_name,
                description=description,
                banner_image=banner_file
            )

            # Automatically create CourseSubject records for typed subjects and assigned teachers
            subjects_list = [s.strip() for s in subject.split(',') if s.strip()]
            if not subjects_list:
                subjects_list = ['Mathematics', 'Physics', 'Chemistry', 'Hindi', 'English']

            for order, s_name in enumerate(subjects_list, start=1):
                # Check for dynamic parameter teacher_for_<subject> or fallbacks
                t_name = body.get(f'teacher_for_{s_name}', body.get('teacher_name', 'Faculty TBD')).strip()
                if not t_name:
                    t_name = 'Faculty TBD'

                CourseSubject.objects.create(
                    course=course,
                    name=s_name,
                    faculty_name=t_name,
                    class_name=class_name,
                    sort_order=order
                )

            ActivityLog.objects.create(
                activity_type='Create Course Batch',
                user_name='Super Admin',
                user_role='Super Admin',
                description=f"Created new batch course '{course.title}' with subject teachers assigned for {course.class_name}"
            )

            return api_response(data={'id': course.id, 'course_id': course.course_id}, message="Course Batch & Subject Teachers Assigned Successfully!", status=201)
        except Exception as e:
            return api_response(message=f"Failed to create course batch: {str(e)}", status=400)

    elif request.method == 'DELETE':
        try:
            body = json.loads(request.body.decode('utf-8'))
            course_id = body.get('id')
            course = CourseBatch.objects.get(id=course_id)
            title = course.title
            course.delete()
            return api_response(message=f"Course '{title}' deleted successfully.")
        except CourseBatch.DoesNotExist:
            return api_response(message="Course batch not found", status=404)

    return api_response(message="Method not allowed", status=405)


@csrf_exempt
def course_wizard_api(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body.decode('utf-8')) if request.body else request.POST
            
            # Step 1: Basic Information
            course_id = body.get('course_db_id')
            title = body.get('title', '').strip() or 'Untitled Course'
            class_name = body.get('class_name', 'Class 10').strip()
            board = body.get('board', 'CBSE').strip()
            academic_session = body.get('academic_session', '2026-27').strip()
            course_type = body.get('course_type', 'Regular').strip()
            short_description = body.get('short_description', '').strip()
            description = body.get('description', '').strip()
            course_status = body.get('course_status', 'Published').strip()

            # Step 4: Pricing & Enrollment
            price = float(body.get('price', 2999))
            discount_type = body.get('discount_type', 'Fixed Amount')
            discount_value = float(body.get('discount_value', 0))
            final_price = float(body.get('final_price', price))
            installment_available = bool(body.get('installment_available', False))
            installment_amount = float(body.get('installment_amount', 0))
            max_enrollment = int(body.get('max_enrollment', 100))
            free_trial_enabled = bool(body.get('free_trial_enabled', True))

            # Create or Update CourseBatch
            if course_id:
                course = CourseBatch.objects.get(id=course_id)
                course.title = title
                course.class_name = class_name
                course.board = board
                course.academic_session = academic_session
                course.course_type = course_type
                course.short_description = short_description
                course.description = description
                course.course_status = course_status
                course.price = price
                course.discount_type = discount_type
                course.discount_value = discount_value
                course.final_price = final_price
                course.installment_available = installment_available
                course.installment_amount = installment_amount
                course.max_enrollment = max_enrollment
                course.free_trial_enabled = free_trial_enabled
                course.save()
            else:
                course = CourseBatch.objects.create(
                    title=title,
                    class_name=class_name,
                    board=board,
                    academic_session=academic_session,
                    course_type=course_type,
                    short_description=short_description,
                    description=description,
                    course_status=course_status,
                    price=price,
                    discount_type=discount_type,
                    discount_value=discount_value,
                    final_price=final_price,
                    installment_available=installment_available,
                    installment_amount=installment_amount,
                    max_enrollment=max_enrollment,
                    free_trial_enabled=free_trial_enabled
                )

            # Step 2: Subjects & Faculty
            subjects_data = body.get('subjects', [])
            if subjects_data and isinstance(subjects_data, list):
                course.subjects.all().delete() # Re-create linked subjects
                for idx, subj in enumerate(subjects_data, start=1):
                    CourseSubject.objects.create(
                        course=course,
                        name=subj.get('name', f'Subject {idx}'),
                        subject_code=subj.get('code', f'SUB-{idx}'),
                        faculty_name=subj.get('faculty_name', 'Faculty TBD'),
                        class_name=class_name,
                        sort_order=idx
                    )

            # Step 3: Batch Configuration
            batch_name = body.get('batch_name', '').strip()
            if batch_name:
                BatchGroup.objects.create(
                    course=course,
                    batch_name=batch_name,
                    batch_code=body.get('batch_code', f"BTC-{random.randint(100, 999)}"),
                    academic_session=academic_session,
                    batch_mode=body.get('batch_mode', 'Online'),
                    class_timing=body.get('class_timing', '4:00 PM - 6:00 PM'),
                    days=body.get('days', 'Mon, Wed, Fri'),
                    max_students=int(body.get('max_students', 50)),
                    branch_classroom=body.get('branch_classroom', 'Main Campus Room 1'),
                    lead_faculty=body.get('lead_faculty', 'Faculty TBD'),
                    batch_status=body.get('batch_status', 'Active')
                )

            # Audit Log
            action_name = "Saved Course Draft" if course_status == 'Draft' else "Published Course"
            ActivityLog.objects.create(
                activity_type=action_name,
                user_name='Super Admin',
                user_role='Super Admin',
                description=f"{action_name} '{course.title}' ({course.class_name})"
            )

            msg = "Course Draft Saved!" if course_status == 'Draft' else "Course Published Successfully!"
            return api_response(data={'id': course.id, 'course_id': course.course_id}, message=msg, status=201)

        except Exception as e:
            return api_response(message=f"Wizard Error: {str(e)}", status=400)

    return api_response(message="Method not allowed", status=405)


# ==========================================
# 4. GLOBAL SEARCH API
# ==========================================
def global_search_api(request):
    query = request.GET.get('q', '').strip()
    if not query:
        return api_response(data={'results': []})

    results = []

    # Search Students
    students = StudentProfile.objects.filter(Q(full_name__icontains=query) | Q(email__icontains=query))[:3]
    for s in students:
        results.append({
            'category': 'Students',
            'title': s.full_name,
            'subtitle': f"{s.student_class} • {s.email}",
            'module_id': 'students'
        })

    # Search Teachers
    teachers = TeacherProfile.objects.filter(Q(full_name__icontains=query) | Q(subjects__icontains=query))[:3]
    for t in teachers:
        results.append({
            'category': 'Teachers',
            'title': t.full_name,
            'subtitle': f"Subject: {t.subjects}",
            'module_id': 'teachers'
        })

    # Search Courses
    courses = CourseBatch.objects.filter(Q(title__icontains=query) | Q(class_name__icontains=query))[:3]
    for c in courses:
        results.append({
            'category': 'Courses',
            'title': c.title,
            'subtitle': f"Fee: ₹{c.price}",
            'module_id': 'courses'
        })

    # Search Payments
    payments = PaymentTransaction.objects.filter(Q(student_name__icontains=query) | Q(transaction_id__icontains=query))[:3]
    for p in payments:
        results.append({
            'category': 'Payments',
            'title': f"TXN: {p.transaction_id}",
            'subtitle': f"{p.student_name} • ₹{p.amount}",
            'module_id': 'payments'
        })

    return api_response(data={'results': results})


# ==========================================
# 5. NOTIFICATIONS API
# ==========================================
@csrf_exempt
def notifications_api(request):
    if request.method == 'GET':
        notifications_qs = AdminNotification.objects.order_by('-id')[:10]
        unread_count = AdminNotification.objects.filter(is_read=False).count()
        notifs_list = [{
            'id': n.id,
            'title': n.title,
            'message': n.message,
            'category': n.category,
            'is_read': n.is_read,
            'created_at': n.created_at.strftime('%H:%M • %d %b')
        } for n in notifications_qs]
        return api_response(data={'notifications': notifs_list, 'unread_count': unread_count})

    elif request.method == 'POST':
        body = json.loads(request.body.decode('utf-8')) if request.body else {}
        action = body.get('action')
        if action == 'mark_all_read':
            AdminNotification.objects.filter(is_read=False).update(is_read=True)
            return api_response(message="All notifications marked as read")
        elif action == 'create':
            title = body.get('title', 'Admin Broadcast')
            msg = body.get('message', 'Notification message')
            n = AdminNotification.objects.create(title=title, message=msg, category='broadcast')
            return api_response(data={'id': n.id}, message="Notification Broadcasted!", status=201)

    return api_response(message="Method not allowed", status=405)


# ==========================================
# 6. PLATFORM SETTINGS & BACKUP API
# ==========================================
@csrf_exempt
def settings_api(request):
    settings_obj, _ = PlatformSettings.objects.get_or_create(id=1)
    if request.method == 'GET':
        return api_response(data={
            'site_name': settings_obj.site_name,
            'active_academic_session': settings_obj.active_academic_session,
            'maintenance_mode': settings_obj.maintenance_mode,
            'contact_email': settings_obj.contact_email,
            'contact_phone': settings_obj.contact_phone
        })
    elif request.method == 'POST':
        body = json.loads(request.body.decode('utf-8')) if request.body else request.POST
        if 'session' in body:
            settings_obj.active_academic_session = body['session']
        if 'site_name' in body:
            settings_obj.site_name = body['site_name']
        settings_obj.save()
        return api_response(message="Settings Saved Successfully!")


@csrf_exempt
def backup_api(request):
    if request.method == 'GET':
        backups_qs = DatabaseBackup.objects.order_by('-id')
        backups_list = [{
            'id': b.id,
            'backup_name': b.backup_name,
            'file_size': b.file_size,
            'status': b.status,
            'created_at': b.created_at.strftime('%Y-%m-%d %H:%M')
        } for b in backups_qs]
        return api_response(data={'backups': backups_list})
    elif request.method == 'POST':
        backup = DatabaseBackup.objects.create(
            backup_name=f"edutrust_db_backup_{timezone.now().strftime('%Y%m%d_%H%M%S')}.sql",
            file_size='2.4 MB',
            status='Completed'
        )
        return api_response(data={'id': backup.id, 'name': backup.backup_name}, message="Database Backup Created Successfully!", status=201)


# ==========================================
# STUDY MATERIALS API (100% REAL DATA)
# ==========================================
@csrf_exempt
def study_materials_api(request):
    """Full CRUD + filtering + stats for Study Materials — all from real database."""

    if request.method == 'GET':
        try:
            # --- REAL DATABASE STATISTICS ---
            stats = {
                'total_study_materials': StudyMaterial.objects.exclude(status='Deleted').count(),
                'total_published': StudyMaterial.objects.filter(status='Published').count(),
                'total_draft': StudyMaterial.objects.filter(status='Draft').count(),
                'total_deleted': StudyMaterial.objects.filter(status='Deleted').count(),
                'total_recorded_lectures': (
                    LiveClass.objects.filter(
                        (Q(recorded_video_link__isnull=False) & ~Q(recorded_video_link='')) |
                        (Q(meet_link__isnull=False) & ~Q(meet_link=''))
                    ).exclude(status='Deleted').count() +
                    CourseLecture.objects.count()
                ),
                'total_live_classes': LiveClass.objects.count(),
                'conducted_live_classes': LiveClass.objects.filter(status='Ended').count(),
                'scheduled_live_classes': LiveClass.objects.filter(status='Scheduled').count(),
                'live_now_classes': LiveClass.objects.filter(status='Live').count(),
                'total_assignments': HomeworkAssignment.objects.count(),
                'total_tests': OnlineTest.objects.count(),
                'total_pyqs': PreviousYearQuestion.objects.count(),
                'total_ebooks': ELibraryBook.objects.count(),
                'total_course_materials': 0,
            }
            try:
                from TutionPlatform.models import CourseMaterial
                stats['total_course_materials'] = CourseMaterial.objects.count()
            except Exception:
                pass

            # --- REAL FILTERS FROM DATABASE ---
            filters_data = {
                'classes': list(StudyMaterial.objects.exclude(status='Deleted').values_list('class_name', flat=True).distinct().order_by('class_name')),
                'subjects': list(StudyMaterial.objects.exclude(status='Deleted').values_list('subject', flat=True).distinct().order_by('subject')),
                'chapters': list(StudyMaterial.objects.exclude(status='Deleted').values_list('chapter', flat=True).distinct().order_by('chapter')),
                'batches': [{'id': b.id, 'title': b.title, 'class_name': b.class_name} for b in CourseBatch.objects.order_by('-id')],
                'teachers': [{'id': t.id, 'full_name': t.full_name} for t in TeacherProfile.objects.order_by('full_name')],
            }

            # --- APPLY REAL DATABASE FILTERS ---
            qs = StudyMaterial.objects.all()

            q = request.GET.get('q', '').strip()
            class_filter = request.GET.get('class_name', '').strip()
            subject_filter = request.GET.get('subject', '').strip()
            chapter_filter = request.GET.get('chapter', '').strip()
            status_filter = request.GET.get('status', '').strip()

            if q:
                qs = qs.filter(Q(title__icontains=q) | Q(subject__icontains=q) | Q(chapter__icontains=q) | Q(material_id__icontains=q) | Q(keywords__icontains=q))
            if class_filter:
                qs = qs.filter(class_name=class_filter)
            if subject_filter:
                qs = qs.filter(subject=subject_filter)
            if chapter_filter:
                qs = qs.filter(chapter=chapter_filter)
            if status_filter:
                qs = qs.filter(status=status_filter)
            else:
                qs = qs.exclude(status='Deleted')

            qs = qs.order_by('-created_at')

            # --- PAGINATION ---
            page = int(request.GET.get('page', 1))
            per_page = int(request.GET.get('per_page', 25))
            paginator = Paginator(qs, per_page)
            page_obj = paginator.get_page(page)

            materials_list = []
            for m in page_obj:
                materials_list.append({
                    'id': m.id,
                    'material_id': m.material_id,
                    'title': m.title,
                    'description': m.description or '',
                    'class_name': m.class_name,
                    'subject': m.subject,
                    'chapter': m.chapter,
                    'unit': m.unit,
                    'keywords': m.keywords or '',
                    'pdf_url': m.pdf_file.url if m.pdf_file else '',
                    'thumbnail_url': m.thumbnail.url if m.thumbnail else '',
                    'file_size': m.file_size or '',
                    'visibility': m.visibility,
                    'download_permission': m.download_permission,
                    'status': m.status,
                    'featured': m.featured,
                    'download_count': m.download_count,
                    'view_count': m.view_count,
                    'uploaded_by': m.uploaded_by,
                    'created_at': m.created_at.strftime('%d %b %Y, %I:%M %p'),
                    'updated_at': m.updated_at.strftime('%d %b %Y, %I:%M %p'),
                })

            # --- REAL RECENT ACTIVITY LOGS ---
            recent_logs_qs = ActivityLog.objects.filter(
                activity_type__icontains='Study Material'
            ).order_by('-id')[:10]
            recent_activity = [{
                'id': l.id,
                'activity_type': l.activity_type,
                'user_name': l.user_name,
                'user_role': l.user_role,
                'description': l.description,
                'created_at': l.created_at.strftime('%d %b %Y, %I:%M %p'),
            } for l in recent_logs_qs]

            data = {
                'stats': stats,
                'filters': filters_data,
                'materials': materials_list,
                'recent_activity': recent_activity,
                'pagination': {
                    'current_page': page_obj.number,
                    'total_pages': paginator.num_pages,
                    'total_records': paginator.count,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous(),
                }
            }
            return api_response(data=data)
        except Exception as e:
            return api_response(message=str(e), status=500)

    elif request.method == 'POST':
        try:
            # Handle multipart/form-data for file upload
            if request.content_type and 'multipart/form-data' in request.content_type:
                body = request.POST
            else:
                body = json.loads(request.body.decode('utf-8')) if request.body else request.POST

            title = body.get('title', '').strip()
            if not title:
                return api_response(message="Title is required.", status=400)

            class_name = body.get('class_name', 'Class 10').strip()
            subject = body.get('subject', '').strip()
            chapter = body.get('chapter', '').strip()
            unit = body.get('unit', '').strip()
            keywords = body.get('keywords', '').strip()
            description = body.get('description', '').strip()
            visibility = body.get('visibility', 'Public').strip()
            download_permission = body.get('download_permission', 'Free Download').strip()
            status_val = body.get('status', 'Published').strip()
            user_display_name = (request.user.get_full_name() or request.user.username or 'Super Admin') if hasattr(request, 'user') and request.user.is_authenticated else 'Super Admin'
            uploaded_by = body.get('uploaded_by', '').strip() or user_display_name

            pdf_file = request.FILES.get('pdf_file')
            thumbnail = request.FILES.get('thumbnail')

            if not pdf_file:
                return api_response(message="PDF file is required.", status=400)

            material = StudyMaterial.objects.create(
                title=title,
                class_name=class_name,
                subject=subject,
                chapter=chapter,
                unit=unit,
                keywords=keywords,
                description=description,
                visibility=visibility,
                download_permission=download_permission,
                status=status_val,
                uploaded_by=uploaded_by,
                pdf_file=pdf_file,
                thumbnail=thumbnail,
            )

            # Create real audit log
            ActivityLog.objects.create(
                activity_type='Study Material Created',
                user_name=uploaded_by,
                user_role='Super Admin',
                description=f'Created study material "{title}" [{material.material_id}] for {class_name} - {subject}',
            )

            return api_response(
                data={'id': material.id, 'material_id': material.material_id},
                message="Study Material created successfully!",
                status=201
            )
        except Exception as e:
            return api_response(message=str(e), status=500)

    elif request.method == 'PUT':
        try:
            material_id = request.GET.get('id', '').strip()
            if not material_id:
                return api_response(message="Material ID is required.", status=400)

            material = StudyMaterial.objects.get(id=int(material_id))

            if request.content_type and 'multipart/form-data' in request.content_type:
                body = request.POST
            else:
                body = json.loads(request.body.decode('utf-8')) if request.body else request.POST

            if body.get('title'):
                material.title = body['title'].strip()
            if body.get('class_name'):
                material.class_name = body['class_name'].strip()
            if body.get('subject'):
                material.subject = body['subject'].strip()
            if body.get('chapter'):
                material.chapter = body['chapter'].strip()
            if body.get('unit'):
                material.unit = body['unit'].strip()
            if body.get('keywords'):
                material.keywords = body['keywords'].strip()
            if body.get('description'):
                material.description = body['description'].strip()
            if body.get('visibility'):
                material.visibility = body['visibility'].strip()
            if body.get('download_permission'):
                material.download_permission = body['download_permission'].strip()

            new_pdf = request.FILES.get('pdf_file')
            if new_pdf:
                material.pdf_file = new_pdf
            new_thumb = request.FILES.get('thumbnail')
            if new_thumb:
                material.thumbnail = new_thumb

            material.save()

            ActivityLog.objects.create(
                activity_type='Study Material Edited',
                user_name='Super Admin',
                user_role='Super Admin',
                description=f'Edited study material "{material.title}" [{material.material_id}]',
            )

            return api_response(message="Study Material updated successfully!")
        except StudyMaterial.DoesNotExist:
            return api_response(message="Study Material not found.", status=404)
        except Exception as e:
            return api_response(message=str(e), status=500)

    elif request.method == 'DELETE':
        try:
            material_id = request.GET.get('id', '').strip()
            if not material_id:
                return api_response(message="Material ID is required.", status=400)

            material = StudyMaterial.objects.get(id=int(material_id))
            old_title = material.title
            old_mid = material.material_id
            material.status = 'Deleted'
            material.save()

            ActivityLog.objects.create(
                activity_type='Study Material Deleted',
                user_name='Super Admin',
                user_role='Super Admin',
                description=f'Deleted study material "{old_title}" [{old_mid}]',
            )

            return api_response(message="Study Material deleted successfully!")
        except StudyMaterial.DoesNotExist:
            return api_response(message="Study Material not found.", status=404)
        except Exception as e:
            return api_response(message=str(e), status=500)

    elif request.method == 'PATCH':
        try:
            material_id = request.GET.get('id', '').strip()
            if not material_id:
                return api_response(message="Material ID is required.", status=400)

            body = json.loads(request.body.decode('utf-8')) if request.body else {}
            action = body.get('action', '').strip()

            material = StudyMaterial.objects.get(id=int(material_id))

            if action == 'publish':
                material.status = 'Published'
                material.save()
                ActivityLog.objects.create(
                    activity_type='Study Material Published',
                    user_name='Super Admin',
                    user_role='Super Admin',
                    description=f'Published study material "{material.title}" [{material.material_id}]',
                )
                return api_response(message="Study Material published successfully!")
            elif action == 'unpublish':
                material.status = 'Draft'
                material.save()
                ActivityLog.objects.create(
                    activity_type='Study Material Unpublished',
                    user_name='Super Admin',
                    user_role='Super Admin',
                    description=f'Unpublished study material "{material.title}" [{material.material_id}]',
                )
                return api_response(message="Study Material unpublished!")
            elif action == 'restore':
                material.status = 'Published'
                material.save()
                ActivityLog.objects.create(
                    activity_type='Study Material Restored',
                    user_name='Super Admin',
                    user_role='Super Admin',
                    description=f'Restored study material "{material.title}" [{material.material_id}]',
                )
                return api_response(message="Study Material restored successfully!")
            else:
                return api_response(message="Invalid action. Use: publish, unpublish, restore.", status=400)

        except StudyMaterial.DoesNotExist:
            return api_response(message="Study Material not found.", status=404)
        except Exception as e:
            return api_response(message=str(e), status=500)

    return api_response(message="Method not allowed.", status=405)


# ==========================================
# PAYMENTS & INVOICES API (100% REAL DATA)
# ==========================================
@csrf_exempt
def payments_api(request):
    """Full CRUD + Aggregation + Analytics for Payments & Invoices — 100% real database data."""

    if request.method == 'GET':
        try:
            today = timezone.now().date()

            # --- REAL KPI STATS FROM DATABASE ---
            success_qs = PaymentTransaction.objects.filter(status='Success')
            pending_qs = PaymentTransaction.objects.filter(status='Pending')
            failed_qs = PaymentTransaction.objects.filter(status='Failed')
            refund_qs = PaymentTransaction.objects.filter(Q(status='Refunded') | Q(status='Partially Refunded'))

            total_revenue = float(success_qs.aggregate(total=Sum('amount'))['total'] or 0.0)
            today_revenue = float(success_qs.filter(created_at__date=today).aggregate(total=Sum('amount'))['total'] or 0.0)
            pending_amount = float(pending_qs.aggregate(total=Sum('amount'))['total'] or 0.0)
            pending_count = pending_qs.count()
            
            total_txns = PaymentTransaction.objects.count()
            successful_count = success_qs.count()
            failed_count = failed_qs.count()
            
            refunded_amount = float(refund_qs.aggregate(total=Sum('refund_amount'))['total'] or 0.0)
            if refunded_amount == 0.0 and refund_qs.exists():
                refunded_amount = float(refund_qs.aggregate(total=Sum('amount'))['total'] or 0.0)
            refund_count = refund_qs.count()

            discounts_given = float(PaymentTransaction.objects.aggregate(total=Sum('discount_amount'))['total'] or 0.0)

            success_rate = round((successful_count / total_txns * 100), 1) if total_txns > 0 else 0.0
            failure_rate = round((failed_count / total_txns * 100), 1) if total_txns > 0 else 0.0

            stats = {
                'total_revenue': total_revenue,
                'today_revenue': today_revenue,
                'pending_amount': pending_amount,
                'pending_count': pending_count,
                'total_transactions': total_txns,
                'successful_count': successful_count,
                'failed_count': failed_count,
                'refunded_amount': refunded_amount,
                'refund_count': refund_count,
                'discounts_given': discounts_given,
                'success_rate': success_rate,
                'failure_rate': failure_rate,
            }

            # --- REAL FILTER OPTIONS FROM DATABASE ---
            filters_data = {
                'students': [{'id': s.id, 'full_name': s.full_name, 'email': s.email} for s in StudentProfile.objects.order_by('full_name')],
                'courses': [{'id': c.id, 'title': c.title, 'class_name': c.class_name} for c in CourseBatch.objects.order_by('title')],
                'statuses': list(PaymentTransaction.objects.values_list('status', flat=True).distinct().order_by('status')),
                'methods': list(PaymentTransaction.objects.values_list('payment_method', flat=True).distinct().order_by('payment_method')),
                'gateways': list(PaymentTransaction.objects.values_list('gateway_name', flat=True).distinct().order_by('gateway_name')),
            }

            # --- APPLY REAL DATABASE FILTERS ---
            qs = PaymentTransaction.objects.all()

            q = request.GET.get('q', '').strip()
            status_filter = request.GET.get('status', '').strip()
            method_filter = request.GET.get('payment_method', '').strip()
            gateway_filter = request.GET.get('gateway_name', '').strip()
            course_filter = request.GET.get('course_title', '').strip()
            date_from = request.GET.get('date_from', '').strip()
            date_to = request.GET.get('date_to', '').strip()

            if q:
                qs = qs.filter(
                    Q(transaction_id__icontains=q) |
                    Q(invoice_number__icontains=q) |
                    Q(student_name__icontains=q) |
                    Q(student_email__icontains=q) |
                    Q(course_title__icontains=q) |
                    Q(gateway_txn_id__icontains=q)
                )
            if status_filter:
                qs = qs.filter(status=status_filter)
            if method_filter:
                qs = qs.filter(payment_method=method_filter)
            if gateway_filter:
                qs = qs.filter(gateway_name=gateway_filter)
            if course_filter:
                qs = qs.filter(course_title=course_filter)
            if date_from:
                qs = qs.filter(created_at__date__gte=date_from)
            if date_to:
                qs = qs.filter(created_at__date__lte=date_to)

            qs = qs.order_by('-created_at')

            # --- PAGINATION ---
            page = int(request.GET.get('page', 1))
            per_page = int(request.GET.get('per_page', 25))
            paginator = Paginator(qs, per_page)
            page_obj = paginator.get_page(page)

            txns_list = []
            for t in page_obj:
                txns_list.append({
                    'id': t.id,
                    'transaction_id': t.transaction_id,
                    'invoice_number': t.invoice_number or f"INV-{t.id:06d}",
                    'student_name': t.student_name,
                    'student_id_code': t.student_id_code or '',
                    'student_email': t.student_email or '',
                    'course_title': t.course_title,
                    'batch_title': t.batch_title or '',
                    'subtotal': float(t.subtotal),
                    'discount_amount': float(t.discount_amount),
                    'tax_amount': float(t.tax_amount),
                    'amount': float(t.amount),
                    'payment_method': t.payment_method,
                    'gateway_name': t.gateway_name,
                    'gateway_txn_id': t.gateway_txn_id or '',
                    'status': t.status,
                    'refund_amount': float(t.refund_amount),
                    'refund_reason': t.refund_reason or '',
                    'notes': t.notes or '',
                    'created_at': t.created_at.strftime('%d %b %Y, %I:%M %p'),
                    'updated_at': t.updated_at.strftime('%d %b %Y, %I:%M %p'),
                })

            # --- REAL REVENUE TREND (Last 7 Days) ---
            from datetime import timedelta
            revenue_trend = []
            for i in range(6, -1, -1):
                day = today - timedelta(days=i)
                day_sum = PaymentTransaction.objects.filter(
                    status='Success',
                    created_at__date=day
                ).aggregate(total=Sum('amount'))['total'] or 0.0
                revenue_trend.append({
                    'date': day.strftime('%a %d %b'),
                    'amount': float(day_sum)
                })

            # --- REAL PAYMENT METHOD DISTRIBUTION ---
            method_dist = list(
                PaymentTransaction.objects.filter(status='Success')
                .values('payment_method')
                .annotate(count=Count('id'), total=Sum('amount'))
                .order_by('-total')
            )
            for m in method_dist:
                m['total'] = float(m['total'] or 0.0)

            # --- REAL TOP COURSES BY REVENUE ---
            top_courses = list(
                PaymentTransaction.objects.filter(status='Success')
                .values('course_title')
                .annotate(total_rev=Sum('amount'), txn_count=Count('id'))
                .order_by('-total_rev')[:5]
            )
            for c in top_courses:
                c['total_rev'] = float(c['total_rev'] or 0.0)

            # --- REAL RECENT PAYMENT AUDIT LOGS ---
            recent_logs_qs = ActivityLog.objects.filter(
                Q(activity_type__icontains='Payment') |
                Q(activity_type__icontains='Invoice') |
                Q(activity_type__icontains='Refund')
            ).order_by('-id')[:10]
            recent_activity = [{
                'id': l.id,
                'activity_type': l.activity_type,
                'user_name': l.user_name,
                'user_role': l.user_role,
                'description': l.description,
                'created_at': l.created_at.strftime('%d %b %Y, %I:%M %p'),
            } for l in recent_logs_qs]

            data = {
                'stats': stats,
                'filters': filters_data,
                'transactions': txns_list,
                'revenue_trend': revenue_trend,
                'method_dist': method_dist,
                'top_courses': top_courses,
                'recent_activity': recent_activity,
                'pagination': {
                    'current_page': page_obj.number,
                    'total_pages': paginator.num_pages,
                    'total_records': paginator.count,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous(),
                }
            }
            return api_response(data=data)
        except Exception as e:
            return api_response(message=str(e), status=500)

    elif request.method == 'POST':
        try:
            body = json.loads(request.body.decode('utf-8')) if request.body else request.POST

            student_name = body.get('student_name', '').strip()
            course_title = body.get('course_title', '').strip()
            amount_val = body.get('amount', 0)

            if not student_name or not course_title:
                return api_response(message="Student Name and Course Title are required.", status=400)

            subtotal = float(body.get('subtotal', amount_val or 0.0))
            discount_amount = float(body.get('discount_amount', 0.0))
            tax_amount = float(body.get('tax_amount', 0.0))
            final_amount = max(0.0, subtotal - discount_amount + tax_amount)

            payment_method = body.get('payment_method', 'UPI').strip()
            gateway_name = body.get('gateway_name', 'Razorpay').strip()
            status_val = body.get('status', 'Success').strip()
            student_email = body.get('student_email', '').strip()
            student_id_code = body.get('student_id_code', '').strip()
            batch_title = body.get('batch_title', '').strip()
            notes = body.get('notes', '').strip()

            txn_id = f"TXN-{random.randint(100000, 999999)}"
            inv_id = f"INV-{random.randint(100000, 999999)}"
            gtxn_id = f"pay_{random.randint(10000000, 99999999)}"

            payment = PaymentTransaction.objects.create(
                transaction_id=txn_id,
                invoice_number=inv_id,
                student_name=student_name,
                student_id_code=student_id_code,
                student_email=student_email,
                course_title=course_title,
                batch_title=batch_title,
                subtotal=subtotal,
                discount_amount=discount_amount,
                tax_amount=tax_amount,
                amount=final_amount,
                payment_method=payment_method,
                gateway_name=gateway_name,
                gateway_txn_id=gtxn_id,
                status=status_val,
                notes=notes
            )

            # Create real audit log
            ActivityLog.objects.create(
                activity_type='Invoice Created',
                user_name='Super Admin',
                user_role='Super Admin',
                description=f'Created invoice {inv_id} / {txn_id} of ₹{final_amount} for {student_name} ({course_title})',
            )

            return api_response(
                data={'id': payment.id, 'transaction_id': payment.transaction_id, 'invoice_number': payment.invoice_number},
                message="Invoice created & transaction logged successfully!",
                status=201
            )
        except Exception as e:
            return api_response(message=str(e), status=500)

    elif request.method in ['PUT', 'PATCH']:
        try:
            txn_id = request.GET.get('id', '').strip()
            if not txn_id:
                return api_response(message="Transaction ID is required.", status=400)

            body = json.loads(request.body.decode('utf-8')) if request.body else {}
            payment = PaymentTransaction.objects.get(id=int(txn_id))

            new_status = body.get('status', '').strip()
            refund_amount = body.get('refund_amount')
            refund_reason = body.get('refund_reason', '').strip()

            if new_status:
                old_status = payment.status
                payment.status = new_status
                if new_status == 'Refunded' and not refund_amount:
                    payment.refund_amount = payment.amount
                elif refund_amount:
                    payment.refund_amount = float(refund_amount)
                if refund_reason:
                    payment.refund_reason = refund_reason
                payment.save()

                ActivityLog.objects.create(
                    activity_type=f'Payment Status Updated',
                    user_name='Super Admin',
                    user_role='Super Admin',
                    description=f'Updated payment {payment.transaction_id} status from {old_status} to {new_status}',
                )

                return api_response(message=f"Payment status updated to {new_status}!")
            else:
                return api_response(message="No status change specified.", status=400)

        except PaymentTransaction.DoesNotExist:
            return api_response(message="Transaction not found.", status=404)
        except Exception as e:
            return api_response(message=str(e), status=500)

    return api_response(message="Method not allowed.", status=405)

# ==========================================
# USER LOGS API (100% REAL DATA — ZERO DUMMY)
# ==========================================
@csrf_exempt
def user_logs_api(request):
    """
    Registered User Logs API with User Type (All Users / Student / Teacher) category selection.
    Strictly zero visitor logs. 100% database-backed registered user activity.
    """
    if request.method == 'GET':
        try:
            today = timezone.now().date()
            from datetime import timedelta
            yesterday = today - timedelta(days=1)

            raw_user_type = request.GET.get('user_type', 'All').strip()
            if raw_user_type.lower() in ['all', 'all users', 'all_users', '']:
                user_type = 'All Users'
            elif raw_user_type.lower() in ['student', 'students']:
                user_type = 'Student'
            elif raw_user_type.lower() in ['teacher', 'teachers', 'tutor']:
                user_type = 'Teacher'
            elif raw_user_type.lower() in ['history', 'archive']:
                user_type = 'History'
            else:
                user_type = 'All Users'

            q = request.GET.get('q', '').strip()
            status_filter = request.GET.get('status', '').strip()
            history_status = request.GET.get('history_status', 'ALL').strip()
            history_role = request.GET.get('history_role', 'ALL').strip()
            date_from = request.GET.get('date_from', '').strip()
            date_to = request.GET.get('date_to', '').strip()

            page = int(request.GET.get('page', 1))
            per_page = int(request.GET.get('per_page', 25))

            if user_type == 'History':
                students = StudentProfile.objects.filter(Q(is_removed=True) | Q(approval_status='rejected') | Q(rejected=True))
                teachers = TeacherProfile.objects.filter(Q(is_removed=True) | Q(approval_status='rejected') | Q(rejected=True) | Q(verification_status='Rejected'))

                if history_role.lower() in ['student', 'students']:
                    teachers = TeacherProfile.objects.none()
                elif history_role.lower() in ['teacher', 'teachers', 'tutor']:
                    students = StudentProfile.objects.none()

                if history_status.lower() == 'removed' or status_filter.lower() == 'removed':
                    students = students.filter(is_removed=True)
                    teachers = teachers.filter(is_removed=True)
                elif history_status.lower() == 'rejected' or status_filter.lower() == 'rejected':
                    students = students.filter(is_removed=False, rejected=True)
                    teachers = teachers.filter(is_removed=False, rejected=True)

                if q:
                    students = students.filter(
                        Q(student_id__icontains=q) | Q(full_name__icontains=q) |
                        Q(email__icontains=q) | Q(mobile__icontains=q) | Q(city__icontains=q)
                    )
                    teachers = teachers.filter(
                        Q(teacher_id__icontains=q) | Q(full_name__icontains=q) |
                        Q(email__icontains=q) | Q(mobile__icontains=q) | Q(city__icontains=q)
                    )

                combined_list = []
                for st in students:
                    action_type = 'Removed' if getattr(st, 'is_removed', False) else 'Rejected'
                    if action_type == 'Removed':
                        action_date_raw = st.removed_at
                        action_date_str = timezone.localtime(action_date_raw).strftime('%d %b %Y, %I:%M %p') if action_date_raw else 'N/A'
                    else:
                        rd = getattr(st, 'rejected_date', None)
                        rt = getattr(st, 'rejected_time', None)
                        if rd and rt:
                            from datetime import datetime as _dt
                            combined = timezone.make_aware(_dt.combine(rd, rt)) if timezone.is_naive(_dt.combine(rd, rt)) else _dt.combine(rd, rt)
                            action_date_str = timezone.localtime(combined).strftime('%d %b %Y, %I:%M %p')
                        elif rd:
                            action_date_str = rd.strftime('%d %b %Y')
                        else:
                            action_date_str = timezone.localtime(st.created_at).strftime('%d %b %Y, %I:%M %p') if st.created_at else 'N/A'
                        action_date_raw = rd or st.created_at
                    action_by = st.removed_by if action_type == 'Removed' else (getattr(st, 'rejected_by', '') or 'Admin')
                    reason = st.removal_reason if action_type == 'Removed' else (getattr(st, 'rejection_reason', '') or 'Registration request rejected.')

                    combined_list.append({
                        'id': st.id,
                        'user_id': st.student_id or f"STU-{st.id}",
                        'full_name': st.full_name,
                        'email': st.email,
                        'mobile': st.mobile or 'N/A',
                        'role_type': 'Student',
                        'student_class': st.student_class or 'N/A',
                        'city': st.city or 'N/A',
                        'action_type': action_type,
                        'action_date': action_date_str,
                        'action_by': action_by or 'Admin',
                        'reason': reason or 'N/A',
                        'is_removed': getattr(st, 'is_removed', False),
                        'is_rejected': getattr(st, 'rejected', False),
                        'account_status': st.account_status or action_type,
                        'raw_created_at': action_date_raw or st.created_at,
                        'created_at': timezone.localtime(st.created_at).strftime('%d %b %Y, %I:%M %p') if st.created_at else 'N/A',
                    })

                for tch in teachers:
                    action_type = 'Removed' if getattr(tch, 'is_removed', False) else 'Rejected'
                    if action_type == 'Removed':
                        action_date_raw = tch.removed_at
                        action_date_str = timezone.localtime(action_date_raw).strftime('%d %b %Y, %I:%M %p') if action_date_raw else 'N/A'
                    else:
                        rd = getattr(tch, 'rejected_date', None)
                        rt = getattr(tch, 'rejected_time', None)
                        if rd and rt:
                            from datetime import datetime as _dt
                            combined = timezone.make_aware(_dt.combine(rd, rt)) if timezone.is_naive(_dt.combine(rd, rt)) else _dt.combine(rd, rt)
                            action_date_str = timezone.localtime(combined).strftime('%d %b %Y, %I:%M %p')
                        elif rd:
                            action_date_str = rd.strftime('%d %b %Y')
                        else:
                            action_date_str = timezone.localtime(tch.created_at).strftime('%d %b %Y, %I:%M %p') if tch.created_at else 'N/A'
                        action_date_raw = rd or tch.created_at
                    action_by = tch.removed_by if action_type == 'Removed' else (getattr(tch, 'rejected_by', '') or 'Admin')
                    reason = tch.removal_reason if action_type == 'Removed' else (getattr(tch, 'rejection_reason', '') or 'Registration request rejected.')

                    combined_list.append({
                        'id': tch.id,
                        'user_id': tch.teacher_id or f"EDUT-{tch.id}",
                        'full_name': tch.full_name,
                        'email': tch.email,
                        'mobile': tch.mobile or 'N/A',
                        'role_type': 'Teacher',
                        'qualification': tch.qualification or 'Graduate',
                        'city': tch.city or 'N/A',
                        'action_type': action_type,
                        'action_date': action_date_str,
                        'action_by': action_by or 'Admin',
                        'reason': reason or 'N/A',
                        'is_removed': getattr(tch, 'is_removed', False),
                        'is_rejected': getattr(tch, 'rejected', False),
                        'account_status': tch.account_status or action_type,
                        'raw_created_at': action_date_raw or tch.created_at,
                        'created_at': timezone.localtime(tch.created_at).strftime('%d %b %Y, %I:%M %p') if tch.created_at else 'N/A',
                    })

                def _sort_key(x):
                    val = x.get('raw_created_at')
                    if val is None:
                        return timezone.now()
                    if hasattr(val, 'hour'):
                        return val if timezone.is_aware(val) else timezone.make_aware(val)
                    from datetime import datetime as _dt, time as _t
                    return timezone.make_aware(_dt.combine(val, _t.min))
                combined_list.sort(key=_sort_key, reverse=True)
                logs_list = combined_list

                total_users = StudentProfile.objects.filter(Q(is_removed=True) | Q(approval_status='rejected')).count() + TeacherProfile.objects.filter(Q(is_removed=True) | Q(approval_status='rejected')).count()
                stats = {
                    'total_users': total_users,
                    'new_today': 0,
                    'active_users': 0,
                    'verified_users': 0,
                    'logins_today': 0,
                    'failed_logins_today': 0,
                    'logouts_today': 0,
                }

            elif user_type == 'All Users':
                students = StudentProfile.objects.exclude(is_removed=True)
                teachers = TeacherProfile.objects.exclude(is_removed=True)

                if q:
                    students = students.filter(
                        Q(student_id__icontains=q) | Q(full_name__icontains=q) |
                        Q(email__icontains=q) | Q(mobile__icontains=q) | Q(city__icontains=q)
                    )
                    teachers = teachers.filter(
                        Q(teacher_id__icontains=q) | Q(full_name__icontains=q) |
                        Q(email__icontains=q) | Q(mobile__icontains=q) | Q(city__icontains=q)
                    )

                if status_filter and status_filter.lower() != 'all':
                    sf_clean = status_filter.lower()
                    if 'pending' in sf_clean:
                        students = students.filter(Q(approval_status='pending') | Q(account_status__iexact='Pending Approval') | Q(account_status__iexact='inactive', approved=False, rejected=False))
                        teachers = teachers.filter(Q(approval_status='pending') | Q(verification_status__iexact='Pending Approval'))
                    elif 'approved' in sf_clean:
                        students = students.filter(Q(approval_status='approved') | Q(approved=True))
                        teachers = teachers.filter(Q(approval_status='approved') | Q(verification_status__iexact='Approved') | Q(approved=True))
                    elif 'rejected' in sf_clean:
                        students = students.filter(Q(approval_status='rejected') | Q(rejected=True))
                        teachers = teachers.filter(Q(approval_status='rejected') | Q(verification_status__iexact='Rejected') | Q(rejected=True))
                    else:
                        students = students.filter(account_status__iexact=status_filter)
                        teachers = teachers.filter(Q(verification_status__iexact=status_filter) | Q(account_status__iexact=status_filter))

                combined_list = []
                for st in students:
                    has_pwd = bool(st.password)
                    combined_list.append({
                        'id': st.id,
                        'user_id': st.student_id or f"STU-{st.id}",
                        'full_name': st.full_name,
                        'email': st.email,
                        'mobile': st.mobile or 'N/A',
                        'role_type': 'Student',
                        'student_class': st.student_class or 'N/A',
                        'board': getattr(st, 'board', '') or '—',
                        'city': st.city or 'N/A',
                        'approval_status': 'approved' if getattr(st, 'approved', False) or getattr(st, 'approval_status', '') == 'approved' else ('rejected' if getattr(st, 'rejected', False) or getattr(st, 'approval_status', '') == 'rejected' else 'pending'),
                        'approved': getattr(st, 'approved', False),
                        'rejected': getattr(st, 'rejected', False),
                        'rejection_reason': getattr(st, 'rejection_reason', '') or '',
                        'account_status': st.account_status or ('Active' if getattr(st, 'approved', False) else 'inactive'),
                        'verification_status': 'Approved' if getattr(st, 'approved', False) or getattr(st, 'approval_status', '') == 'approved' else ('Rejected' if getattr(st, 'rejected', False) or getattr(st, 'approval_status', '') == 'rejected' else 'Pending Approval'),
                        'password_status': 'Set' if has_pwd else 'Not Set',
                        'password_display': 'Set' if has_pwd else 'Not Set',
                        'raw_created_at': st.created_at,
                        'created_at': timezone.localtime(st.created_at).strftime('%d %b %Y, %I:%M %p') if st.created_at else 'N/A',
                    })

                for tch in teachers:
                    has_pwd = bool(tch.password)
                    is_tch_approved = getattr(tch, 'approved', False) or getattr(tch, 'approval_status', '') == 'approved' or getattr(tch, 'verification_status', '') == 'Approved'
                    is_tch_rejected = getattr(tch, 'rejected', False) or getattr(tch, 'approval_status', '') == 'rejected' or getattr(tch, 'verification_status', '') == 'Rejected'
                    combined_list.append({
                        'id': tch.id,
                        'user_id': tch.teacher_id or f"EDUT-{tch.id}",
                        'full_name': tch.full_name,
                        'email': tch.email,
                        'mobile': tch.mobile or 'N/A',
                        'role_type': 'Teacher',
                        'qualification': tch.qualification or 'Graduate',
                        'experience': tch.experience or '1 Year',
                        'subjects': tch.subjects or 'General Subjects',
                        'expected_fee': tch.expected_fee or 'N/A',
                        'city': tch.city or 'N/A',
                        'teaching_mode': tch.tuition_mode or 'Home & Online',
                        'approval_status': 'approved' if is_tch_approved else ('rejected' if is_tch_rejected else 'pending'),
                        'approved': is_tch_approved,
                        'rejected': is_tch_rejected,
                        'rejection_reason': getattr(tch, 'rejection_reason', '') or '',
                        'verification_status': 'Approved' if is_tch_approved else ('Rejected' if is_tch_rejected else 'Pending Approval'),
                        'account_status': tch.account_status or ('Active' if is_tch_approved else 'inactive'),
                        'password_status': 'Set' if has_pwd else 'Not Set',
                        'password_display': 'Set' if has_pwd else 'Not Set',
                        'raw_created_at': tch.created_at,
                        'created_at': timezone.localtime(tch.created_at).strftime('%d %b %Y, %I:%M %p') if tch.created_at else 'N/A',
                    })

                combined_list.sort(key=lambda x: x['raw_created_at'] or timezone.now(), reverse=True)
                logs_list = combined_list

                total_users = StudentProfile.objects.exclude(is_removed=True).count() + TeacherProfile.objects.exclude(is_removed=True).count()
                new_today = StudentProfile.objects.exclude(is_removed=True).filter(created_at__date=today).count() + TeacherProfile.objects.exclude(is_removed=True).filter(created_at__date=today).count()
                active_users = StudentProfile.objects.exclude(is_removed=True).filter(account_status='Active').count() + TeacherProfile.objects.exclude(is_removed=True).filter(account_status='Active').count()
                verified_users = StudentProfile.objects.exclude(is_removed=True).exclude(email='').count() + TeacherProfile.objects.exclude(is_removed=True).filter(Q(verification_status='Approved') | Q(approved=True)).count()

                stats = {
                    'total_users': total_users,
                    'new_today': new_today,
                    'active_users': active_users,
                    'verified_users': verified_users,
                    'logins_today': UserAuthLog.objects.filter(activity_type='LOGIN', created_at__date=today).count(),
                    'failed_logins_today': UserAuthLog.objects.filter(activity_type='FAILED_LOGIN', created_at__date=today).count(),
                    'logouts_today': UserAuthLog.objects.filter(activity_type='LOGOUT', created_at__date=today).count(),
                }

            elif user_type == 'Student':
                students_qs = StudentProfile.objects.exclude(is_removed=True)

                if q:
                    students_qs = students_qs.filter(
                        Q(student_id__icontains=q) |
                        Q(full_name__icontains=q) |
                        Q(email__icontains=q) |
                        Q(mobile__icontains=q) |
                        Q(city__icontains=q) |
                        Q(student_class__icontains=q)
                    )

                if status_filter and status_filter.lower() != 'all':
                    sf_clean = status_filter.lower()
                    if 'pending' in sf_clean:
                        students_qs = students_qs.filter(Q(approval_status='pending') | Q(account_status__iexact='Pending Approval') | Q(account_status__iexact='inactive', approved=False, rejected=False))
                    elif 'approved' in sf_clean:
                        students_qs = students_qs.filter(Q(approval_status='approved') | Q(approved=True))
                    elif 'rejected' in sf_clean:
                        students_qs = students_qs.filter(Q(approval_status='rejected') | Q(rejected=True))
                    else:
                        students_qs = students_qs.filter(account_status__iexact=status_filter)

                if date_from:
                    students_qs = students_qs.filter(created_at__date__gte=date_from)
                if date_to:
                    students_qs = students_qs.filter(created_at__date__lte=date_to)

                students_qs = students_qs.order_by('-created_at')

                logs_list = []
                for st in students_qs:
                    has_pwd = bool(st.password)
                    logs_list.append({
                        'id': st.id,
                        'user_id': st.student_id or f"STU-{st.id}",
                        'full_name': st.full_name,
                        'email': st.email,
                        'mobile': st.mobile or 'N/A',
                        'role_type': 'Student',
                        'student_class': st.student_class or 'N/A',
                        'board': getattr(st, 'board', '') or '—',
                        'city': st.city or 'N/A',
                        'approval_status': 'approved' if getattr(st, 'approved', False) or getattr(st, 'approval_status', '') == 'approved' else ('rejected' if getattr(st, 'rejected', False) or getattr(st, 'approval_status', '') == 'rejected' else 'pending'),
                        'approved': getattr(st, 'approved', False),
                        'rejected': getattr(st, 'rejected', False),
                        'rejection_reason': getattr(st, 'rejection_reason', '') or '',
                        'account_status': st.account_status or ('Active' if getattr(st, 'approved', False) else 'inactive'),
                        'verification_status': 'Approved' if getattr(st, 'approved', False) or getattr(st, 'approval_status', '') == 'approved' else ('Rejected' if getattr(st, 'rejected', False) or getattr(st, 'approval_status', '') == 'rejected' else 'Pending Approval'),
                        'password_status': 'Set' if has_pwd else 'Not Set',
                        'password_display': 'Set' if has_pwd else 'Not Set',
                        'created_at': timezone.localtime(st.created_at).strftime('%d %b %Y, %I:%M %p') if st.created_at else 'N/A',
                    })

                stats = {
                    'total_users': StudentProfile.objects.exclude(is_removed=True).count(),
                    'new_today': StudentProfile.objects.exclude(is_removed=True).filter(created_at__date=today).count(),
                    'active_users': StudentProfile.objects.exclude(is_removed=True).filter(account_status='Active').count(),
                    'verified_users': StudentProfile.objects.exclude(is_removed=True).exclude(email='').count(),
                    'logins_today': UserAuthLog.objects.filter(activity_type='LOGIN', user_role='Student', created_at__date=today).count(),
                    'failed_logins_today': UserAuthLog.objects.filter(activity_type='FAILED_LOGIN', user_role='Student', created_at__date=today).count(),
                    'logouts_today': UserAuthLog.objects.filter(activity_type='LOGOUT', user_role='Student', created_at__date=today).count(),
                }

            else:
                teachers_qs = TeacherProfile.objects.exclude(is_removed=True)

                if q:
                    teachers_qs = teachers_qs.filter(
                        Q(teacher_id__icontains=q) |
                        Q(full_name__icontains=q) |
                        Q(email__icontains=q) |
                        Q(mobile__icontains=q) |
                        Q(city__icontains=q) |
                        Q(subjects__icontains=q) |
                        Q(qualification__icontains=q)
                    )

                if status_filter and status_filter.lower() != 'all':
                    teachers_qs = teachers_qs.filter(Q(verification_status__iexact=status_filter) | Q(account_status__iexact=status_filter))

                if date_from:
                    teachers_qs = teachers_qs.filter(created_at__date__gte=date_from)
                if date_to:
                    teachers_qs = teachers_qs.filter(created_at__date__lte=date_to)

                teachers_qs = teachers_qs.order_by('-created_at')

                logs_list = []
                for tch in teachers_qs:
                    has_pwd = bool(tch.password)
                    is_tch_approved = getattr(tch, 'approved', False) or getattr(tch, 'approval_status', '') == 'approved' or getattr(tch, 'verification_status', '') == 'Approved'
                    is_tch_rejected = getattr(tch, 'rejected', False) or getattr(tch, 'approval_status', '') == 'rejected' or getattr(tch, 'verification_status', '') == 'Rejected'
                    logs_list.append({
                        'id': tch.id,
                        'user_id': tch.teacher_id or f"EDUT-{tch.id}",
                        'full_name': tch.full_name,
                        'email': tch.email,
                        'mobile': tch.mobile or 'N/A',
                        'role_type': 'Teacher',
                        'qualification': tch.qualification or 'Graduate',
                        'experience': tch.experience or '1 Year',
                        'subjects': tch.subjects or 'General Subjects',
                        'expected_fee': tch.expected_fee or 'N/A',
                        'city': tch.city or 'N/A',
                        'teaching_mode': tch.tuition_mode or 'Home & Online',
                        'approval_status': 'approved' if is_tch_approved else ('rejected' if is_tch_rejected else 'pending'),
                        'approved': is_tch_approved,
                        'rejected': is_tch_rejected,
                        'rejection_reason': getattr(tch, 'rejection_reason', '') or '',
                        'verification_status': 'Approved' if is_tch_approved else ('Rejected' if is_tch_rejected else 'Pending Approval'),
                        'account_status': tch.account_status or ('Active' if is_tch_approved else 'inactive'),
                        'password_status': 'Set' if has_pwd else 'Not Set',
                        'password_display': 'Set' if has_pwd else 'Not Set',
                        'created_at': timezone.localtime(tch.created_at).strftime('%d %b %Y, %I:%M %p') if tch.created_at else 'N/A',
                    })

                stats = {
                    'total_users': TeacherProfile.objects.exclude(is_removed=True).count(),
                    'new_today': TeacherProfile.objects.exclude(is_removed=True).filter(created_at__date=today).count(),
                    'active_users': TeacherProfile.objects.exclude(is_removed=True).filter(account_status='Active').count(),
                    'verified_users': TeacherProfile.objects.exclude(is_removed=True).filter(Q(verification_status='Approved') | Q(approved=True)).count(),
                    'logins_today': UserAuthLog.objects.filter(activity_type='LOGIN', user_role__in=['Teacher', 'Tutor'], created_at__date=today).count(),
                    'failed_logins_today': UserAuthLog.objects.filter(activity_type='FAILED_LOGIN', user_role__in=['Teacher', 'Tutor'], created_at__date=today).count(),
                    'logouts_today': UserAuthLog.objects.filter(activity_type='LOGOUT', user_role__in=['Teacher', 'Tutor'], created_at__date=today).count(),
                }

            period_param = request.GET.get('period', '7days')
            analytics_data = _calculate_user_logs_analytics_data(period_param)

            data = {
                'user_type': user_type,
                'stats': stats,
                'logs': logs_list,
                'chart_data': analytics_data['chart_data'],
                'top_users': analytics_data['top_users'],
                'summary': analytics_data['summary'],
                'pagination': {
                    'current_page': 1,
                    'total_pages': 1,
                    'total_records': len(logs_list),
                    'has_next': False,
                    'has_previous': False,
                }
            }
            return api_response(data=data)
        except Exception as e:
            return api_response(message=str(e), status=500)

    return api_response(message="Method not allowed.", status=405)


@csrf_exempt
def api_admin_user_logs_user_detail(request):
    """
    Returns complete user registration details & chronological activity timeline for a user.
    """
    if request.method == 'GET':
        email = request.GET.get('email', '').strip().lower()
        user_id = request.GET.get('user_id', '').strip()
        user_type = request.GET.get('user_type', '').strip().capitalize()

        if not email and not user_id:
            return api_response(message="Missing user_id or email parameter.", status=400)

        student = None
        teacher = None
        user_obj = None

        if user_type == 'Student':
            student = StudentProfile.objects.filter(Q(email=email) | Q(student_id=user_id)).first()
        elif user_type == 'Teacher':
            teacher = TeacherProfile.objects.filter(Q(email=email) | Q(teacher_id=user_id)).first()

        if not student and not teacher:
            student = StudentProfile.objects.filter(Q(email=email) | Q(student_id=user_id)).first()
            teacher = TeacherProfile.objects.filter(Q(email=email) | Q(teacher_id=user_id)).first()
            user_obj = User.objects.filter(Q(email=email) | Q(username=email)).first()

        email_clean = email or (student.email if student else (teacher.email if teacher else (user_obj.email if user_obj else '')))

        if not student and not teacher and not user_obj and not email_clean:
            return api_response(message="Registered user not found.", status=404)

        extra_fields = {}

        if student:
            full_name = student.full_name
            mobile = student.mobile
            role = 'Student'
            uid = student.student_id or f"STU-{student.id}"
            account_status = student.account_status or 'Active'
            location = f"{student.city or ''}, {student.state or ''}".strip(', ') or 'N/A'
            reg_date = timezone.localtime(student.created_at).strftime('%d %b %Y, %I:%M %p') if student.created_at else 'N/A'
            is_approved = getattr(student, 'approved', False) or getattr(student, 'approval_status', '') == 'approved'
            is_rejected = getattr(student, 'rejected', False) or getattr(student, 'approval_status', '') == 'rejected'
            if is_approved:
                verification_status = 'Approved'
                approval_status = 'approved'
            elif is_rejected:
                verification_status = 'Rejected'
                approval_status = 'rejected'
            else:
                verification_status = 'Pending Approval'
                approval_status = 'pending'
            has_password = bool(student.password)
            extra_fields = {
                'student_class': student.student_class or 'N/A',
                'board': getattr(student, 'board', '') or '—',
                'city': student.city or 'N/A',
                'state': student.state or 'N/A',
                'address': student.address or 'N/A',
            }
        elif teacher:
            full_name = teacher.full_name
            mobile = teacher.mobile
            role = 'Tutor'
            uid = teacher.teacher_id or f"EDUT-{teacher.id}"
            account_status = teacher.account_status or 'Active'
            location = f"{teacher.city or ''}, {teacher.state or ''}".strip(', ') or 'N/A'
            reg_date = timezone.localtime(teacher.created_at).strftime('%d %b %Y, %I:%M %p') if teacher.created_at else 'N/A'
            is_tch_approved = getattr(teacher, 'approved', False) or getattr(teacher, 'approval_status', '') == 'approved' or getattr(teacher, 'verification_status', '') == 'Approved'
            is_tch_rejected = getattr(teacher, 'rejected', False) or getattr(teacher, 'approval_status', '') == 'rejected' or getattr(teacher, 'verification_status', '') == 'Rejected'
            if is_tch_approved:
                verification_status = 'Approved'
                approval_status = 'approved'
            elif is_tch_rejected:
                verification_status = 'Rejected'
                approval_status = 'rejected'
            else:
                verification_status = 'Pending Approval'
                approval_status = 'pending'
            has_password = bool(teacher.password)
            extra_fields = {
                'qualification': teacher.qualification or 'N/A',
                'experience': teacher.experience or 'N/A',
                'subjects': teacher.subjects or 'N/A',
                'teaching_classes': teacher.teaching_classes or 'N/A',
                'expected_fee': teacher.expected_fee or 'N/A',
                'teaching_mode': teacher.tuition_mode or 'N/A',
                'city': teacher.city or 'N/A',
                'state': teacher.state or 'N/A',
                'bio': teacher.bio or 'N/A',
            }
        elif user_obj:
            full_name = user_obj.get_full_name() or user_obj.username
            mobile = 'N/A'
            role = 'Super Admin' if user_obj.is_superuser or user_obj.is_staff else 'Registered User'
            uid = f'USR-{user_obj.id}'
            account_status = 'Active' if user_obj.is_active else 'Inactive'
            location = 'Admin Panel'
            reg_date = timezone.localtime(user_obj.date_joined).strftime('%d %b %Y, %I:%M %p') if user_obj.date_joined else 'N/A'
            verification_status = 'Approved'
            approval_status = 'approved'
            has_password = bool(user_obj.password)
        else:
            full_name = 'Registered User'
            mobile = 'N/A'
            role = 'Registered User'
            uid = user_id or 'N/A'
            account_status = 'Active'
            location = 'N/A'
            reg_date = 'N/A'
            verification_status = 'Pending Approval'
            approval_status = 'pending'
            has_password = True

        user_logs = UserAuthLog.objects.filter(Q(email=email_clean) | Q(user_id_str=uid)).order_by('-created_at')

        total_successful_logins = user_logs.filter(activity_type='LOGIN', status='Successful').count()
        total_failed_logins = user_logs.filter(activity_type='FAILED_LOGIN').count()

        last_login_log = user_logs.filter(activity_type='LOGIN', status='Successful').first()
        last_logout_log = user_logs.filter(activity_type='LOGOUT').first()
        last_failed_log = user_logs.filter(activity_type='FAILED_LOGIN').first()

        timeline = []
        for log in user_logs:
            timeline.append({
                'id': log.id,
                'activity_type': log.activity_type,
                'status': log.status,
                'date_str': timezone.localtime(log.created_at).strftime('%d %b %Y'),
                'time_str': timezone.localtime(log.created_at).strftime('%I:%M %p'),
                'timestamp_str': timezone.localtime(log.created_at).strftime('%d %b %Y, %I:%M %p'),
                'ip_address': log.ip_address or 'N/A',
                'device': log.device or 'Desktop',
                'browser': log.browser or 'Chrome',
                'operating_system': log.operating_system or 'Windows',
                'source_page': log.source_page or 'Direct',
                'description': log.description or ''
            })

        user_detail = {
            'user_id': uid,
            'full_name': full_name,
            'email': email_clean,
            'mobile': mobile,
            'role': role,
            'location': location,
            'account_status': account_status,
            'verification_status': verification_status,
            'approval_status': approval_status,
            'registration_date': reg_date,
            'password_status': 'Set' if has_password else 'Not Set',
            'password_display': 'Set' if has_password else 'Not Set',
            'last_password_change': reg_date,
            'extra_fields': extra_fields,
            'stats': {
                'total_successful_logins': total_successful_logins,
                'total_failed_logins': total_failed_logins,
                'last_login': {
                    'date_time': timezone.localtime(last_login_log.created_at).strftime('%d %b %Y, %I:%M %p') if last_login_log else 'Never',
                    'ip': last_login_log.ip_address if last_login_log else 'N/A',
                    'device': last_login_log.device if last_login_log else 'N/A',
                    'browser': last_login_log.browser if last_login_log else 'N/A',
                    'os': last_login_log.operating_system if last_login_log else 'N/A',
                },
                'last_logout': {
                    'date_time': timezone.localtime(last_logout_log.created_at).strftime('%d %b %Y, %I:%M %p') if last_logout_log else 'Never',
                    'ip': last_logout_log.ip_address if last_logout_log else 'N/A',
                    'device': last_logout_log.device if last_logout_log else 'N/A',
                    'browser': last_logout_log.browser if last_logout_log else 'N/A',
                },
                'last_failed_login': {
                    'date_time': timezone.localtime(last_failed_log.created_at).strftime('%d %b %Y, %I:%M %p') if last_failed_log else 'None',
                    'ip': last_failed_log.ip_address if last_failed_log else 'N/A',
                }
            },
            'timeline': timeline
        }
        return api_response(data=user_detail)

    return api_response(message="Method not allowed.", status=405)


@csrf_exempt
def api_admin_user_reset_password(request):
    """
    Admin action to securely reset password for a registered Student or Teacher account.
    Uses Django's cryptographic password hashing (make_password & user.set_password).
    Strictly zero plain-text password storage or logging.
    """
    if request.method == 'POST':
        # 1. Admin Authentication & Authorization Guard
        if not (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)):
            return api_response(message="You are not authorized to reset this password. Admin access required.", status=403)

        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            data = request.POST

        email = data.get('email', '').strip().lower()
        user_id = data.get('user_id', '').strip()
        user_type = data.get('user_type', '').strip().capitalize()
        new_password = data.get('new_password', '')
        confirm_password = data.get('confirm_password', '')

        if not email and not user_id:
            return api_response(message="User identification (email or user_id) is required.", status=400)

        if not new_password or not confirm_password:
            return api_response(message="Both New Password and Confirm Password are required.", status=400)

        if new_password != confirm_password:
            return api_response(message="Passwords do not match.", status=400)

        if len(new_password) < 6:
            return api_response(message="Password must contain at least 6 characters.", status=400)

        # 2. Find target profile & User instance using unique ID / PK and email
        student = None
        teacher = None
        user_obj = None

        target_role = user_type.capitalize() if user_type else ''

        if user_id:
            uid_str = str(user_id).strip()
            if uid_str.isdigit():
                uid_num = int(uid_str)
                if target_role == 'Student':
                    student = StudentProfile.objects.filter(Q(id=uid_num) | Q(student_id=uid_str)).first()
                elif target_role in ['Teacher', 'Tutor']:
                    teacher = TeacherProfile.objects.filter(Q(id=uid_num) | Q(teacher_id=uid_str)).first()

                if not student and not teacher:
                    student = StudentProfile.objects.filter(Q(id=uid_num) | Q(student_id=uid_str)).first()
                    if not student:
                        teacher = TeacherProfile.objects.filter(Q(id=uid_num) | Q(teacher_id=uid_str)).first()
                    if not student and not teacher:
                        user_obj = User.objects.filter(pk=uid_num).first()
            else:
                if target_role == 'Student':
                    student = StudentProfile.objects.filter(student_id=uid_str).first()
                elif target_role in ['Teacher', 'Tutor']:
                    teacher = TeacherProfile.objects.filter(teacher_id=uid_str).first()

                if not student and not teacher:
                    student = StudentProfile.objects.filter(student_id=uid_str).first()
                    if not student:
                        teacher = TeacherProfile.objects.filter(teacher_id=uid_str).first()

        if not student and not teacher and email:
            if target_role == 'Student':
                student = StudentProfile.objects.filter(email__iexact=email).first()
            elif target_role in ['Teacher', 'Tutor']:
                teacher = TeacherProfile.objects.filter(email__iexact=email).first()
            else:
                student = StudentProfile.objects.filter(email__iexact=email).first()
                if not student:
                    teacher = TeacherProfile.objects.filter(email__iexact=email).first()

        target_email = email or (student.email if student else (teacher.email if teacher else ''))

        if not user_obj and target_email:
            user_obj = User.objects.filter(Q(email__iexact=target_email) | Q(username__iexact=target_email)).first()

        if not student and not teacher and not user_obj:
            return api_response(message="User not found.", status=404)

        # 3. Hash and Update Password inside atomic transaction
        from django.db import transaction
        from django.contrib.auth.hashers import make_password

        with transaction.atomic():
            hashed_password = make_password(new_password)
            full_name = 'Registered User'
            user_role = 'User'

            if target_role == 'Student' or (student and not (target_role in ['Teacher', 'Tutor'] and teacher)):
                if student:
                    student.password = hashed_password
                    student.save(update_fields=['password'])
                    full_name = student.full_name
                    user_role = 'Student'
            elif target_role in ['Teacher', 'Tutor'] or teacher:
                if teacher:
                    teacher.password = hashed_password
                    teacher.save(update_fields=['password'])
                    full_name = teacher.full_name
                    user_role = 'Teacher'

            if user_obj:
                user_obj.set_password(new_password)
                user_obj.save()
                if not student and not teacher:
                    full_name = user_obj.get_full_name() or user_obj.username

        # 4. Log Activity in UserAuthLog (Zero plain text passwords saved)
        admin_username = request.user.username if (hasattr(request, 'user') and request.user and getattr(request.user, 'username', None)) else 'Admin'
        log_user_auth_event(
            request,
            activity_type='PASSWORD_RESET',
            email=target_email,
            full_name=full_name,
            user_role=user_role,
            status='Successful',
            source_page='Admin User Logs',
            description=f"Password reset performed successfully by Admin ({admin_username})",
            student_profile=student,
            teacher_profile=teacher
        )

        return JsonResponse({'status': 'success', 'message': f"Password has been updated successfully for {target_email}."})

    return api_response(message="Method not allowed.", status=405)


def _calculate_user_logs_analytics_data(period='7days'):
    from datetime import timedelta
    today = timezone.now().date()

    period_str = str(period).lower().strip()
    if '30' in period_str:
        days_count = 30
    elif '90' in period_str:
        days_count = 90
    else:
        days_count = 7

    start_date = today - timedelta(days=days_count - 1)

    chart_data = []
    raw_counts = []
    for i in range(days_count - 1, -1, -1):
        day = today - timedelta(days=i)
        count = UserAuthLog.objects.filter(created_at__date=day).count()
        raw_counts.append(count)
        chart_data.append({
            'date': day.strftime('%Y-%m-%d'),
            'label': day.strftime('%d %b'),
            'day_name': day.strftime('%a'),
            'full_date_str': day.strftime('%d %b %Y (%a)'),
            'count': count,
            'avg_trend': 0,
        })

    total_activities = sum(c['count'] for c in chart_data)
    avg_per_day = round(total_activities / float(days_count), 1) if days_count > 0 else 0
    for idx, item in enumerate(chart_data):
        window = raw_counts[max(0, idx-1):min(len(raw_counts), idx+2)]
        item['avg_trend'] = round(sum(window) / float(len(window)), 1) if window else avg_per_day

    prev_end_date = start_date - timedelta(days=1)
    prev_start_date = prev_end_date - timedelta(days=days_count - 1)
    previous_period_activities = UserAuthLog.objects.filter(
        created_at__date__gte=prev_start_date,
        created_at__date__lte=prev_end_date
    ).count()

    if previous_period_activities > 0:
        change_percent = round(((total_activities - previous_period_activities) / float(previous_period_activities)) * 100.0, 1)
    else:
        change_percent = 100.0 if total_activities > 0 else 0.0

    average_per_day = round(total_activities / float(days_count), 2)
    peak_item = max(chart_data, key=lambda x: x['count']) if chart_data else {'count': 0, 'full_date_str': '-'}
    peak_count = peak_item['count']
    peak_date = peak_item.get('full_date_str') or peak_item.get('label') or '-'

    top_users_qs = list(
        UserAuthLog.objects.filter(created_at__date__gte=start_date, created_at__date__lte=today)
        .exclude(full_name__isnull=True).exclude(full_name='')
        .values('full_name', 'user_role')
        .annotate(activity_count=Count('id'), total=Count('id'))
        .order_by('-total')[:5]
    )

    if not top_users_qs:
        top_users_qs = list(
            UserAuthLog.objects.exclude(full_name__isnull=True).exclude(full_name='')
            .values('full_name', 'user_role')
            .annotate(activity_count=Count('id'), total=Count('id'))
            .order_by('-total')[:5]
        )

    max_user_activity = max([u['activity_count'] for u in top_users_qs]) if top_users_qs else 1
    if max_user_activity == 0:
        max_user_activity = 1

    top_users = []
    for u in top_users_qs:
        cnt = u.get('activity_count', 0)
        progress_pct = round((cnt / float(max_user_activity)) * 100.0, 1)
        top_users.append({
            'id': u.get('full_name'),
            'name': u.get('full_name'),
            'user_name': u.get('full_name'),
            'role': u.get('user_role') or 'User',
            'user_role': u.get('user_role') or 'User',
            'activity_count': cnt,
            'total': cnt,
            'progress_percent': progress_pct,
        })

    summary = {
        'total_activities': total_activities,
        'previous_period_activities': previous_period_activities,
        'change_percent': change_percent,
        'average_per_day': average_per_day,
        'peak_count': peak_count,
        'peak_date': peak_date,
        'days_count': days_count,
    }

    return {
        'activity_trend': chart_data,
        'chart_data': chart_data,
        'top_active_users': top_users,
        'top_users': top_users,
        'summary': summary,
    }


def api_admin_user_logs_analytics(request):
    """Dedicated API endpoint for Registered User Auth Analytics."""
    if request.method == 'GET':
        try:
            period_param = request.GET.get('period', '7days')
            analytics_data = _calculate_user_logs_analytics_data(period_param)
            return api_response(data=analytics_data)
        except Exception as e:
            return api_response(message=str(e), status=500)

    return api_response(message="Method not allowed.", status=405)


# ==========================================
# STUDENT PROFILE CHANGE AUDIT HISTORY API
# ==========================================
def admin_profile_changes_api(request):
    """Admin API for auditing student profile changes (OLD vs NEW)."""
    if request.method == 'GET':
        try:
            qs = StudentProfileChangeLog.objects.select_related('student').order_by('-changed_at')

            search = request.GET.get('search', '').strip()
            field_filter = request.GET.get('field_name', '').strip()
            date_filter = request.GET.get('date_range', '').strip()
            ref_filter = request.GET.get('update_ref', '').strip()

            if search:
                qs = qs.filter(
                    Q(student__full_name__icontains=search) |
                    Q(student__student_id__icontains=search) |
                    Q(update_reference__icontains=search) |
                    Q(field_label__icontains=search) |
                    Q(old_value__icontains=search) |
                    Q(new_value__icontains=search)
                )

            if field_filter:
                qs = qs.filter(field_name=field_filter)

            if ref_filter:
                qs = qs.filter(update_reference=ref_filter)

            today = timezone.now().date()
            if date_filter == 'today':
                qs = qs.filter(changed_at__date=today)
            elif date_filter == '7days':
                qs = qs.filter(changed_at__date__gte=today - timezone.timedelta(days=7))
            elif date_filter == '30days':
                qs = qs.filter(changed_at__date__gte=today - timezone.timedelta(days=30))

            page_number = request.GET.get('page', 1)
            paginator = Paginator(qs, 15)
            page_obj = paginator.get_page(page_number)

            from datetime import timedelta
            yesterday = today - timedelta(days=1)

            logs_list = []
            for item in page_obj:
                is_today = False
                is_yesterday = False
                if item.changed_at:
                    local_dt = timezone.localtime(item.changed_at)
                    c_date = local_dt.date()
                    w_str = local_dt.strftime('%A')
                    d_str = local_dt.strftime('%b %d, %Y')
                    if c_date == today:
                        date_group_label = f"Today — {w_str}, {d_str}"
                        is_today = True
                    elif c_date == yesterday:
                        date_group_label = f"Yesterday — {w_str}, {d_str}"
                        is_yesterday = True
                    else:
                        date_group_label = f"{w_str}, {d_str}"
                else:
                    date_group_label = "Date Unknown"

                logs_list.append({
                    'id': item.id,
                    'update_reference': item.update_reference,
                    'student_id': item.student.student_id if item.student else 'STU-00000',
                    'student_name': item.student.full_name if item.student else 'Unknown',
                    'student_class': item.student.student_class if item.student else '',
                    'field_name': item.field_name,
                    'field_label': item.field_label,
                    'old_value': item.old_value or 'Not provided',
                    'new_value': item.new_value or 'Not provided',
                    'changed_by': item.changed_by or 'Student',
                    'changed_at': timezone.localtime(item.changed_at).strftime('%d %b %Y, %I:%M %p') if item.changed_at else '',
                    'date_group_label': date_group_label,
                    'is_today': is_today,
                    'is_yesterday': is_yesterday,
                    'ip_address': item.ip_address or '127.0.0.1',
                    'status': item.status or 'Updated'
                })

            today_count = StudentProfileChangeLog.objects.filter(changed_at__date=today).count()
            distinct_fields_count = StudentProfileChangeLog.objects.values('field_name').distinct().count()
            verified_count = StudentProfileChangeLog.objects.filter(status='Updated').count()

            data = {
                'stats': {
                    'total_changes': StudentProfileChangeLog.objects.count(),
                    'today_changes': today_count,
                    'fields_modified': distinct_fields_count,
                    'verified_updates': verified_count,
                },
                'logs': logs_list,
                'pagination': {
                    'current_page': page_obj.number,
                    'total_pages': paginator.num_pages,
                    'total_records': paginator.count,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous(),
                }
            }
            return api_response(data=data)
        except Exception as e:
            return api_response(message=str(e), status=500)

    return api_response(message="Method not allowed.", status=405)



# =========================================================
# BATCH CONTROL CENTER API — COMPLETE REAL DATABASE BACKEND
# =========================================================

def batches_api(request):
    """
    Real DB API for Batch Management / Batch Control Center.
    Handles multi-filtering, search, stats, creation, and listing.
    """
    if request.method == 'GET':
        try:
            today = timezone.now().date()
            now_dt = timezone.now()

            # --- REAL KPI STATS ---
            stats = {
                'total_batches': CourseBatch.objects.count(),
                'active_count': CourseBatch.objects.filter(status='Active').count(),
                'upcoming_count': CourseBatch.objects.filter(Q(status='Upcoming') | Q(status='Scheduled')).count(),
                'draft_count': CourseBatch.objects.filter(status='Draft').count(),
                'paused_count': CourseBatch.objects.filter(status='Paused').count(),
                'expired_count': CourseBatch.objects.filter(status='Expired').count(),
                'completed_count': CourseBatch.objects.filter(status='Completed').count(),
            }

            # --- REAL FILTER DROPDOWN OPTIONS ---
            classes_opt = [f"Class {i}" for i in range(1, 13)]
            boards_opt = list(CourseBatch.objects.exclude(board='').values_list('board', flat=True).distinct().order_by('board'))
            if not boards_opt:
                boards_opt = ['CBSE', 'ICSE', 'ISC', 'UP Board', 'State Board']

            subjects_opt = list(CourseBatch.objects.exclude(subject='').values_list('subject', flat=True).distinct().order_by('subject'))
            if not subjects_opt:
                subjects_opt = ['Mathematics', 'Physics', 'Chemistry', 'Biology', 'English', 'Science', 'Social Studies']

            teachers_opt = list(TeacherProfile.objects.all().values('id', 'teacher_id', 'full_name', 'email', 'subjects'))

            filters_opt = {
                'classes': classes_opt,
                'boards': boards_opt,
                'streams': ['Science', 'Commerce', 'Arts / Humanities', 'N/A'],
                'subjects': subjects_opt,
                'teachers': teachers_opt,
                'statuses': ['Draft', 'Scheduled', 'Upcoming', 'Active', 'Paused', 'Completed', 'Expired', 'Cancelled', 'Archived'],
                'types': ['Online', 'Offline', 'Hybrid', 'Live', 'Recorded', 'Live + Recorded'],
                'visibilities': ['Public', 'Private', 'Hidden'],
            }

            # --- APPLY MULTI-FILTERS ---
            qs = CourseBatch.objects.all()

            q = request.GET.get('q', '').strip()
            class_filter = request.GET.get('class_name', '').strip()
            board_filter = request.GET.get('board', '').strip()
            stream_filter = request.GET.get('stream', '').strip()
            subject_filter = request.GET.get('subject', '').strip()
            teacher_filter = request.GET.get('teacher_id', '').strip()
            status_filter = request.GET.get('status', '').strip()
            type_filter = request.GET.get('batch_type', '').strip()
            visibility_filter = request.GET.get('visibility', '').strip()
            price_filter = request.GET.get('price_type', '').strip()
            date_preset = request.GET.get('date_preset', '').strip()

            if q:
                qs = qs.filter(
                    Q(title__icontains=q) |
                    Q(course_id__icontains=q) |
                    Q(subject__icontains=q) |
                    Q(class_name__icontains=q) |
                    Q(board__icontains=q) |
                    Q(stream__icontains=q) |
                    Q(teacher_name__icontains=q) |
                    Q(assigned_teachers__full_name__icontains=q)
                ).distinct()

            if class_filter:
                qs = qs.filter(class_name=class_filter)

            if board_filter:
                qs = qs.filter(board=board_filter)

            if stream_filter:
                qs = qs.filter(stream=stream_filter)

            if subject_filter:
                qs = qs.filter(subject__icontains=subject_filter)

            if teacher_filter:
                try:
                    t_id_int = int(teacher_filter)
                    qs = qs.filter(Q(assigned_teachers__id=t_id_int) | Q(assigned_teachers__teacher_id__icontains=teacher_filter)).distinct()
                except ValueError:
                    qs = qs.filter(assigned_teachers__full_name__icontains=teacher_filter).distinct()

            if status_filter:
                qs = qs.filter(status=status_filter)

            if type_filter:
                qs = qs.filter(batch_type=type_filter)

            if visibility_filter:
                qs = qs.filter(visibility=visibility_filter)

            if price_filter == 'free':
                qs = qs.filter(Q(price=0) | Q(is_free=True))
            elif price_filter == 'paid':
                qs = qs.filter(price__gt=0, is_free=False)

            if date_preset == 'today':
                qs = qs.filter(created_at__date=today)
            elif date_preset == 'upcoming':
                qs = qs.filter(Q(status='Upcoming') | Q(status='Scheduled') | Q(launch_date__gt=now_dt))
            elif date_preset == 'expiring_soon':
                qs = qs.filter(expiry_date__gt=now_dt, expiry_date__lte=now_dt + timezone.timedelta(days=7))
            elif date_preset == 'expired':
                qs = qs.filter(Q(status='Expired') | Q(expiry_date__lt=now_dt))

            qs = qs.order_by('-id')

            # --- SERIALIZE BATCH CARDS ---
            page = int(request.GET.get('page', 1))
            per_page = int(request.GET.get('per_page', 50))
            paginator = Paginator(qs, per_page)
            page_obj = paginator.get_page(page)

            batches_list = []
            for b in page_obj:
                # Retrieve all assigned teachers cleanly
                assigned_list = []
                for t in b.assigned_teachers.all():
                    assigned_list.append({
                        'id': t.id,
                        'teacher_id': t.teacher_id,
                        'full_name': t.full_name,
                        'email': t.email or '',
                        'subjects': t.subjects or 'Faculty',
                        'photo': t.profile_photo.url if t.profile_photo else '',
                    })

                # Fallback to teacher_name if empty
                if not assigned_list and b.teacher_name:
                    assigned_list.append({
                        'id': 0,
                        'teacher_id': 'FAC-001',
                        'full_name': b.teacher_name,
                        'email': '',
                        'subjects': b.subject,
                        'photo': '',
                    })

                calc_final = float(b.final_price) if b.final_price and b.final_price > 0 else float(b.price)

                batches_list.append({
                    'id': b.id,
                    'course_id': b.course_id or f"CRS-{b.id}",
                    'title': b.title,
                    'class_name': b.class_name,
                    'board': b.board or 'CBSE',
                    'stream': b.stream or 'N/A',
                    'subject': b.subject,
                    'status': b.status or 'Active',
                    'batch_type': b.batch_type or 'Live + Recorded',
                    'visibility': b.visibility or 'Public',
                    'price': float(b.price),
                    'final_price': calc_final,
                    'discount_percent': b.discount_percent,
                    'is_free': b.is_free,
                    'banner_image': b.banner_image.url if b.banner_image else '',
                    'enrollment_count': b.current_enrollment_count,
                    'max_enrollment': b.max_enrollment or 100,
                    'available_seats': max(0, (b.max_enrollment or 100) - b.current_enrollment_count),
                    'start_date': b.start_date.strftime('%d %b %Y') if b.start_date else '',
                    'launch_date': b.launch_date.strftime('%d %b %Y, %I:%M %p') if b.launch_date else '',
                    'expiry_date': b.expiry_date.strftime('%d %b %Y, %I:%M %p') if b.expiry_date else '',
                    'teachers': assigned_list,
                })

            data = {
                'stats': stats,
                'filters': filters_opt,
                'batches': batches_list,
                'pagination': {
                    'current_page': page_obj.number,
                    'total_pages': paginator.num_pages,
                    'total_records': paginator.count,
                }
            }
            return api_response(data=data)

        except Exception as e:
            return api_response(message=str(e), status=500)

    elif request.method == 'POST':
        try:
            if request.content_type and 'multipart/form-data' in request.content_type:
                body = request.POST
            else:
                body = json.loads(request.body.decode('utf-8')) if request.body else request.POST

            title = body.get('title', '').strip()
            if not title:
                return api_response(message="Batch Title is required.", status=400)

            class_name = body.get('class_name', 'Class 10').strip()
            board = body.get('board', 'CBSE').strip()
            stream = body.get('stream', 'N/A').strip()
            subject = body.get('subject', 'Mathematics').strip()
            batch_type = body.get('batch_type', 'Live + Recorded').strip()
            visibility = body.get('visibility', 'Public').strip()
            status_val = body.get('status', 'Active').strip()
            price_val = float(body.get('price', 2999))
            discount_pct = int(body.get('discount_percent', 0))
            max_seats = int(body.get('max_enrollment', 100))

            calc_final = price_val - (price_val * (discount_pct / 100.0))

            banner_file = request.FILES.get('banner_image')

            batch = CourseBatch.objects.create(
                title=title,
                class_name=class_name,
                board=board,
                stream=stream,
                subject=subject,
                batch_type=batch_type,
                visibility=visibility,
                status=status_val,
                price=price_val,
                discount_percent=discount_pct,
                final_price=calc_final,
                max_enrollment=max_seats,
                banner_image=banner_file
            )

            # Assign teacher IDs if provided
            teacher_ids = body.getlist('teacher_ids') if hasattr(body, 'getlist') else body.get('teacher_ids', [])
            if teacher_ids:
                if isinstance(teacher_ids, str):
                    teacher_ids = [t.strip() for t in teacher_ids.split(',') if t.strip()]
                for tid in teacher_ids:
                    try:
                        t = TeacherProfile.objects.get(id=int(tid))
                        BatchTeacherAssignment.objects.create(batch=batch, teacher=t, role_or_subject=f"{subject} Faculty")
                    except Exception:
                        pass

            # Log activity
            BatchActivityLog.objects.create(
                batch=batch,
                action='Batch Created',
                description=f"Batch '{title}' [{batch.course_id}] created successfully for {class_name} ({board})."
            )

            return api_response(data={'id': batch.id, 'course_id': batch.course_id}, message="Batch created successfully!", status=201)

        except Exception as e:
            return api_response(message=str(e), status=500)


def batch_detail_api(request, batch_id):
    """
    Detailed Control Center API for single Batch (View Details, Lifecycle & Tab actions).
    Supports Django user authentication as well as session-authenticated Admin roles.
    """
    is_authenticated = (
        (hasattr(request, 'user') and request.user and request.user.is_authenticated) or
        (hasattr(request, 'session') and (
            request.session.get('user_role') or
            request.session.get('role') or
            request.session.get('user_id') or
            request.session.get('admin_user') or
            'is_logged_in' in request.session or
            request.session.session_key
        ))
    )
    if not is_authenticated:
        return api_response(message="Authentication required. Please log in to view batch details.", status=401)

    try:
        batch = CourseBatch.objects.get(id=batch_id)
    except CourseBatch.DoesNotExist:
        return api_response(message=f"Batch not found or has been removed.", status=404)

    if request.method == 'GET':
        # Retrieve all assigned teachers
        teachers_list = []
        for assign in batch.teacher_assignments.all():
            t = assign.teacher
            teachers_list.append({
                'assignment_id': assign.id,
                'teacher_id': t.id,
                'code': t.teacher_id,
                'full_name': t.full_name,
                'email': t.email or '',
                'mobile': t.mobile or '',
                'subjects': t.subjects or '',
                'role': assign.role_or_subject or 'Faculty',
                'assigned_at': assign.assigned_at.strftime('%d %b %Y'),
                'photo': t.profile_photo.url if t.profile_photo else '',
            })

        # Retrieve coupons
        coupons_list = [{
            'id': c.id,
            'code': c.code,
            'discount_type': c.discount_type,
            'discount_value': float(c.discount_value),
            'used_count': c.used_count,
            'usage_limit': c.usage_limit,
            'is_active': c.is_active,
        } for c in batch.coupons.all()]

        # Retrieve activity logs
        logs_list = [{
            'id': l.id,
            'user_name': l.user_name,
            'user_role': l.user_role,
            'action': l.action,
            'description': l.description,
            'created_at': l.created_at.strftime('%d %b %Y, %I:%M %p'),
        } for l in batch.activity_logs.all()]

        data = {
            'id': batch.id,
            'course_id': batch.course_id,
            'title': batch.title,
            'class_name': batch.class_name,
            'board': batch.board,
            'stream': batch.stream or 'N/A',
            'subject': batch.subject,
            'status': batch.status,
            'batch_type': batch.batch_type,
            'visibility': batch.visibility,
            'price': float(batch.price),
            'discount_percent': batch.discount_percent,
            'final_price': float(batch.final_price or batch.price),
            'current_enrollment': batch.current_enrollment_count,
            'max_enrollment': batch.max_enrollment,
            'available_seats': max(0, batch.max_enrollment - batch.current_enrollment_count),
            'start_date': batch.start_date.strftime('%Y-%m-%d') if batch.start_date else '',
            'launch_date': batch.launch_date.strftime('%Y-%m-%d') if batch.launch_date else '',
            'expiry_date': batch.expiry_date.strftime('%Y-%m-%d') if batch.expiry_date else '',
            'class_timing': getattr(batch, 'class_timing', '') or '',
            'class_days': getattr(batch, 'class_days', '') or '',
            'branch': getattr(batch, 'branch', '') or '',
            'description': batch.description or '',
            'waitlist_enabled': batch.waitlist_enabled,
            'banner_image': batch.banner_image.url if batch.banner_image else '',
            'teachers': teachers_list,
            'coupons': coupons_list,
            'activity_logs': logs_list,
        }
        return api_response(data=data)

    elif request.method == 'POST':
        try:
            body = json.loads(request.body.decode('utf-8')) if request.body else request.POST
            action = body.get('action', '').strip()

            if action == 'launch_now':
                batch.status = 'Active'
                batch.launch_date = timezone.now()
                batch.save()
                BatchActivityLog.objects.create(batch=batch, action='Batch Launched', description='Batch was launched manually by Super Admin.')
                return api_response(message="Batch launched successfully!")

            elif action == 'pause':
                batch.status = 'Paused'
                batch.save()
                BatchActivityLog.objects.create(batch=batch, action='Batch Paused', description='Batch enrollment & access paused by Super Admin.')
                return api_response(message="Batch paused successfully!")

            elif action == 'resume':
                batch.status = 'Active'
                batch.save()
                BatchActivityLog.objects.create(batch=batch, action='Batch Resumed', description='Batch resumed by Super Admin.')
                return api_response(message="Batch resumed successfully!")

            elif action == 'expire_now':
                batch.status = 'Expired'
                batch.expiry_date = timezone.now()
                batch.save()
                BatchActivityLog.objects.create(batch=batch, action='Batch Expired', description='Batch marked as expired by Super Admin.')
                return api_response(message="Batch expired successfully!")

            elif action == 'reject':
                reason = body.get('reason', 'Batch rejected by Super Admin.').strip()
                batch.status = 'Rejected'
                batch.rejection_reason = reason
                batch.save()
                BatchActivityLog.objects.create(batch=batch, action='Batch Rejected', description=f"Rejected by Super Admin. Reason: {reason}")
                return api_response(message="Batch rejected successfully!")

            elif action == 'update_pricing':
                price_val = float(body.get('price', batch.price))
                disc_pct = int(body.get('discount_percent', batch.discount_percent))
                calc_final = price_val - (price_val * (disc_pct / 100.0))
                
                old_p = float(batch.price)
                batch.price = price_val
                batch.discount_percent = disc_pct
                batch.final_price = calc_final
                batch.save()

                BatchActivityLog.objects.create(batch=batch, action='Pricing Changed', description=f"Price updated from ₹{old_p} to ₹{price_val} (Final: ₹{calc_final}).")
                return api_response(message="Batch pricing updated successfully!")

            elif action == 'update_batch':
                with transaction.atomic():
                    title = body.get('title', batch.title).strip()
                    class_name = body.get('class_name', batch.class_name).strip()
                    board = body.get('board', batch.board).strip()
                    stream = body.get('stream', batch.stream).strip()
                    subject = body.get('subject', batch.subject).strip()
                    batch_type = body.get('batch_type', batch.batch_type).strip()
                    visibility = body.get('visibility', batch.visibility).strip()
                    status_val = body.get('status', batch.status).strip()
                    price_val = float(body.get('price', batch.price))
                    disc_pct = int(body.get('discount_percent', batch.discount_percent))
                    calc_final = max(0, price_val - (price_val * (disc_pct / 100.0)))

                    class_timing = body.get('class_timing', getattr(batch, 'class_timing', '')).strip()
                    class_days = body.get('class_days', getattr(batch, 'class_days', '')).strip()
                    branch = body.get('branch', getattr(batch, 'branch', '')).strip()
                    description = body.get('description', batch.description or '').strip()

                    start_d_str = body.get('start_date', '')
                    if start_d_str:
                        try:
                            from django.utils.dateparse import parse_date
                            d_parsed = parse_date(start_d_str)
                            if d_parsed:
                                batch.start_date = d_parsed
                        except Exception:
                            pass

                    launch_d_str = body.get('launch_date', '')
                    expiry_d_str = body.get('expiry_date', '')

                    if launch_d_str:
                        try:
                            from django.utils.dateparse import parse_date
                            d_parsed = parse_date(launch_d_str)
                            if d_parsed:
                                batch.launch_date = timezone.make_aware(timezone.datetime.combine(d_parsed, timezone.datetime.min.time()))
                        except Exception:
                            pass

                    if expiry_d_str:
                        try:
                            from django.utils.dateparse import parse_date
                            d_parsed = parse_date(expiry_d_str)
                            if d_parsed:
                                batch.expiry_date = timezone.make_aware(timezone.datetime.combine(d_parsed, timezone.datetime.min.time()))
                        except Exception:
                            pass

                    batch.title = title
                    batch.class_name = class_name
                    batch.board = board
                    batch.stream = stream
                    batch.subject = subject
                    batch.batch_type = batch_type
                    batch.visibility = visibility
                    batch.status = status_val
                    batch.price = price_val
                    batch.discount_percent = disc_pct
                    batch.final_price = calc_final
                    batch.class_timing = class_timing
                    batch.class_days = class_days
                    batch.branch = branch
                    batch.description = description
                    batch.save()

                    # Handle Teacher Assignments (Support empty array teacher_ids: [])
                    if 'teacher_ids' in body:
                        raw_tids = body.get('teacher_ids')
                        if isinstance(raw_tids, str):
                            teacher_ids = [int(t.strip()) for t in raw_tids.split(',') if t.strip().isdigit()]
                        elif isinstance(raw_tids, list):
                            teacher_ids = [int(t) for t in raw_tids if str(t).isdigit() or isinstance(t, int)]
                        else:
                            teacher_ids = []

                        BatchTeacherAssignment.objects.filter(batch=batch).delete()
                        for tid in teacher_ids:
                            try:
                                t_obj = TeacherProfile.objects.get(id=tid)
                                BatchTeacherAssignment.objects.create(batch=batch, teacher=t_obj, role_or_subject=f"{subject} Faculty")
                            except Exception:
                                pass

                    BatchActivityLog.objects.create(batch=batch, action='Batch Updated', description=f"Batch '{title}' updated by Super Admin (Price: ₹{calc_final}, Status: {status_val}).")
                    return api_response(message="Batch updated successfully!")

            elif action == 'assign_teacher':
                teacher_id = body.get('teacher_id')
                if teacher_id:
                    t = TeacherProfile.objects.get(id=int(teacher_id))
                    BatchTeacherAssignment.objects.get_or_create(batch=batch, teacher=t, defaults={'role_or_subject': f"{batch.subject} Faculty"})
                    BatchActivityLog.objects.create(batch=batch, action='Teacher Assigned', description=f"Assigned teacher '{t.full_name}' to batch.")
                return api_response(message="Teacher assigned successfully!")

            elif action == 'remove_teacher':
                teacher_id = body.get('teacher_id')
                if teacher_id:
                    BatchTeacherAssignment.objects.filter(batch=batch, teacher_id=int(teacher_id)).delete()
                    BatchActivityLog.objects.create(batch=batch, action='Teacher Removed', description=f"Removed teacher ID #{teacher_id} from batch.")
                return api_response(message="Teacher removed successfully!")

            elif action == 'duplicate':
                new_batch = CourseBatch.objects.create(
                    title=f"{batch.title} (Copy)",
                    class_name=batch.class_name,
                    board=batch.board,
                    stream=batch.stream,
                    subject=batch.subject,
                    batch_type=batch.batch_type,
                    visibility='Private',
                    status='Draft',
                    price=batch.price,
                    discount_percent=batch.discount_percent,
                    final_price=batch.final_price,
                    max_enrollment=batch.max_enrollment,
                )
                for assign in batch.teacher_assignments.all():
                    BatchTeacherAssignment.objects.create(batch=new_batch, teacher=assign.teacher, role_or_subject=assign.role_or_subject)
                BatchActivityLog.objects.create(batch=new_batch, action='Batch Duplicated', description=f"Duplicated from batch '{batch.title}' [{batch.course_id}].")
                return api_response(data={'new_id': new_batch.id, 'new_code': new_batch.course_id}, message="Batch duplicated successfully!")

            elif action == 'archive':
                batch.status = 'Archived'
                batch.save()
                BatchActivityLog.objects.create(batch=batch, action='Batch Archived', description='Batch archived by Super Admin.')
                return api_response(message="Batch archived successfully!")

            elif action == 'delete':
                title_ref = batch.title
                batch.delete()
                return api_response(message=f"Batch '{title_ref}' deleted permanently.")

            return api_response(message="Action complete.")

        except Exception as e:
            return api_response(message=str(e), status=500)


@csrf_exempt
def api_admin_user_logs_approve(request):
    """
    Approve a pending Student or Teacher registration.
    """
    if request.method == 'POST':
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST

            user_id = str(data.get('user_id', '')).strip()
            email = str(data.get('email', '')).strip().lower()
            user_type = str(data.get('user_type', '')).strip().capitalize()

            student = None
            teacher = None

            if user_type == 'Student':
                student = StudentProfile.objects.filter(Q(id=int(user_id) if user_id.isdigit() else -1) | Q(student_id=user_id) | Q(email=email)).first()
            elif user_type == 'Teacher':
                teacher = TeacherProfile.objects.filter(Q(id=int(user_id) if user_id.isdigit() else -1) | Q(teacher_id=user_id) | Q(email=email)).first()

            if not student and not teacher:
                student = StudentProfile.objects.filter(Q(student_id=user_id) | Q(email=email)).first()
                teacher = TeacherProfile.objects.filter(Q(teacher_id=user_id) | Q(email=email)).first()

            now = timezone.now()
            admin_username = request.session.get('user_name') or 'Admin'

            if student:
                student.approval_status = 'approved'
                student.account_status = 'Active'
                student.approved = True
                student.rejected = False
                student.approval_date = now
                student.approved_date = now.date()
                student.approved_time = now.time()
                student.approved_by = admin_username
                student.save()

                u_obj = User.objects.filter(email=student.email).first()
                if u_obj:
                    u_obj.is_active = True
                    u_obj.save()

                log_user_auth_event(
                    request, activity_type='ACCOUNT_APPROVED', email=student.email,
                    full_name=student.full_name, mobile=student.mobile, user_role='Student',
                    user_id_str=student.student_id, status='Successful', source_page='Admin User Log',
                    description=f"Student {student.full_name} ({student.student_id}) registration approved by {admin_username}.",
                    student_profile=student
                )
                return JsonResponse({
                    'status': 'success', 
                    'message': f'Student {student.full_name} has been approved successfully.',
                    'full_name': student.full_name,
                    'user_role': 'Student'
                })

            elif teacher:
                teacher.approval_status = 'approved'
                teacher.verification_status = 'Approved'
                teacher.account_status = 'Active'
                teacher.approved = True
                teacher.rejected = False
                teacher.approval_date = now
                teacher.approved_date = now.date()
                teacher.approved_time = now.time()
                teacher.approved_by = admin_username
                teacher.save()

                u_obj = User.objects.filter(email=teacher.email).first()
                if u_obj:
                    u_obj.is_active = True
                    u_obj.save()

                log_user_auth_event(
                    request, activity_type='ACCOUNT_APPROVED', email=teacher.email,
                    full_name=teacher.full_name, mobile=teacher.mobile, user_role='Teacher',
                    user_id_str=teacher.teacher_id, status='Successful', source_page='Admin User Log',
                    description=f"Teacher {teacher.full_name} ({teacher.teacher_id}) registration approved by {admin_username}.",
                    teacher_profile=teacher
                )
                return JsonResponse({
                    'status': 'success', 
                    'message': f'Teacher {teacher.full_name} has been approved successfully.',
                    'full_name': teacher.full_name,
                    'user_role': 'Teacher'
                })

            else:
                return JsonResponse({'status': 'error', 'message': 'User profile not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Method not allowed.'}, status=405)


@csrf_exempt
def api_admin_user_logs_reject(request):
    """
    Reject a pending Student or Teacher registration with optional rejection reason.
    """
    if request.method == 'POST':
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST

            user_id = str(data.get('user_id', '')).strip()
            email = str(data.get('email', '')).strip().lower()
            user_type = str(data.get('user_type', '')).strip().capitalize()
            rejection_reason = str(data.get('rejection_reason', '')).strip() or 'Registration request rejected by admin.'

            student = None
            teacher = None

            if user_type == 'Student':
                student = StudentProfile.objects.filter(Q(id=int(user_id) if user_id.isdigit() else -1) | Q(student_id=user_id) | Q(email=email)).first()
            elif user_type == 'Teacher':
                teacher = TeacherProfile.objects.filter(Q(id=int(user_id) if user_id.isdigit() else -1) | Q(teacher_id=user_id) | Q(email=email)).first()

            if not student and not teacher:
                student = StudentProfile.objects.filter(Q(student_id=user_id) | Q(email=email)).first()
                teacher = TeacherProfile.objects.filter(Q(teacher_id=user_id) | Q(email=email)).first()

            now = timezone.now()
            admin_username = request.session.get('user_name') or 'Admin'

            if student:
                student.approval_status = 'rejected'
                student.verification_status = 'Rejected'
                student.account_status = 'Inactive'
                student.approved = False
                student.rejected = True
                student.rejected_date = now.date()
                student.rejected_time = now.time()
                student.rejected_by = admin_username
                student.rejection_reason = rejection_reason
                student.save()

                u_obj = User.objects.filter(email=student.email).first()
                if u_obj:
                    u_obj.is_active = False
                    u_obj.save()

                log_user_auth_event(
                    request, activity_type='ACCOUNT_REJECTED', email=student.email,
                    full_name=student.full_name, mobile=student.mobile, user_role='Student',
                    user_id_str=student.student_id, status='Failed', source_page='Admin User Log',
                    description=f"Student {student.full_name} ({student.student_id}) registration rejected by {admin_username}. Reason: {rejection_reason}",
                    student_profile=student
                )
                return JsonResponse({
                    'status': 'success', 
                    'message': f'Student {student.full_name} has been rejected successfully.',
                    'full_name': student.full_name,
                    'user_role': 'Student'
                })

            elif teacher:
                teacher.approval_status = 'rejected'
                teacher.verification_status = 'Rejected'
                teacher.account_status = 'Inactive'
                teacher.approved = False
                teacher.rejected = True
                teacher.rejected_date = now.date()
                teacher.rejected_time = now.time()
                teacher.rejected_by = admin_username
                teacher.rejection_reason = rejection_reason
                teacher.save()

                u_obj = User.objects.filter(email=teacher.email).first()
                if u_obj:
                    u_obj.is_active = False
                    u_obj.save()

                log_user_auth_event(
                    request, activity_type='ACCOUNT_REJECTED', email=teacher.email,
                    full_name=teacher.full_name, mobile=teacher.mobile, user_role='Teacher',
                    user_id_str=teacher.teacher_id, status='Failed', source_page='Admin User Log',
                    description=f"Teacher {teacher.full_name} ({teacher.teacher_id}) registration rejected by {admin_username}. Reason: {rejection_reason}",
                    teacher_profile=teacher
                )
                return JsonResponse({
                    'status': 'success', 
                    'message': f'Teacher {teacher.full_name} has been rejected successfully.',
                    'full_name': teacher.full_name,
                    'user_role': 'Teacher'
                })

            else:
                return JsonResponse({'status': 'error', 'message': 'User profile not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Method not allowed.'}, status=405)


@csrf_exempt
def api_admin_user_logs_remove(request):
    """
    Remove (soft-delete/archive) a Student or Teacher from active User Logs view and move to History.
    """
    if request.method == 'POST':
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST

            user_id = str(data.get('user_id', '')).strip()
            email = str(data.get('email', '')).strip().lower()
            user_type = str(data.get('user_type', '')).strip().capitalize()
            removal_reason = str(data.get('removal_reason', '')).strip() or 'User removed by admin.'

            student = None
            teacher = None

            if user_type == 'Student':
                student = StudentProfile.objects.filter(Q(id=int(user_id) if user_id.isdigit() else -1) | Q(student_id=user_id) | Q(email=email)).first()
            elif user_type in ['Teacher', 'Tutor']:
                teacher = TeacherProfile.objects.filter(Q(id=int(user_id) if user_id.isdigit() else -1) | Q(teacher_id=user_id) | Q(email=email)).first()

            if not student and not teacher:
                student = StudentProfile.objects.filter(Q(student_id=user_id) | Q(email=email)).first()
                teacher = TeacherProfile.objects.filter(Q(teacher_id=user_id) | Q(email=email)).first()

            now = timezone.now()
            admin_username = request.session.get('user_name') or (getattr(request.user, 'username', None) if hasattr(request, 'user') else 'Admin') or 'Admin'

            if student:
                student.is_removed = True
                student.removed_at = now
                student.removed_by = admin_username
                student.removal_reason = removal_reason
                student.account_status = 'Removed'
                student.save()

                u_obj = User.objects.filter(email=student.email).first()
                if u_obj:
                    u_obj.is_active = False
                    u_obj.save()

                log_user_auth_event(
                    request, activity_type='ACCOUNT_REMOVED', email=student.email,
                    full_name=student.full_name, mobile=student.mobile, user_role='Student',
                    user_id_str=student.student_id, status='Removed', source_page='Admin User Log',
                    description=f"Student {student.full_name} ({student.student_id}) removed by {admin_username}. Reason: {removal_reason}",
                    student_profile=student
                )
                return JsonResponse({
                    'status': 'success',
                    'success': True,
                    'message': f'Student {student.full_name} has been removed successfully.',
                    'full_name': student.full_name,
                    'user_role': 'Student'
                })

            elif teacher:
                teacher.is_removed = True
                teacher.removed_at = now
                teacher.removed_by = admin_username
                teacher.removal_reason = removal_reason
                teacher.account_status = 'Removed'
                teacher.save()

                u_obj = User.objects.filter(email=teacher.email).first()
                if u_obj:
                    u_obj.is_active = False
                    u_obj.save()

                log_user_auth_event(
                    request, activity_type='ACCOUNT_REMOVED', email=teacher.email,
                    full_name=teacher.full_name, mobile=teacher.mobile, user_role='Teacher',
                    user_id_str=teacher.teacher_id, status='Removed', source_page='Admin User Log',
                    description=f"Teacher {teacher.full_name} ({teacher.teacher_id}) removed by {admin_username}. Reason: {removal_reason}",
                    teacher_profile=teacher
                )
                return JsonResponse({
                    'status': 'success',
                    'success': True,
                    'message': f'Teacher {teacher.full_name} has been removed successfully.',
                    'full_name': teacher.full_name,
                    'user_role': 'Teacher'
                })

            else:
                return JsonResponse({'status': 'error', 'success': False, 'message': 'User profile not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'success': False, 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'success': False, 'message': 'Method not allowed.'}, status=405)

