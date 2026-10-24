from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import json, re, logging
from .models import FreeTrialBooking
from TutionPlatform.models import ActivityLog, AdminNotification, StudentProfile

logger = logging.getLogger(__name__)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip or '127.0.0.1'


def parse_system_info(user_agent):
    if not user_agent:
        return 'Unknown Browser', 'Unknown OS', 'Desktop'
    
    # Device Type
    if 'mobi' in user_agent.lower() or 'android' in user_agent.lower() or 'iphone' in user_agent.lower():
        device_type = 'Mobile'
    elif 'ipad' in user_agent.lower() or 'tablet' in user_agent.lower():
        device_type = 'Tablet'
    else:
        device_type = 'Desktop'

    # OS
    if 'Windows' in user_agent:
        os_name = 'Windows'
    elif 'Android' in user_agent:
        os_name = 'Android'
    elif 'iPhone' in user_agent or 'iPad' in user_agent or 'Mac OS' in user_agent:
        os_name = 'iOS/MacOS'
    elif 'Linux' in user_agent:
        os_name = 'Linux'
    else:
        os_name = 'Other'

    # Browser
    if 'Chrome' in user_agent and 'Edg' not in user_agent:
        browser_name = 'Chrome'
    elif 'Firefox' in user_agent:
        browser_name = 'Firefox'
    elif 'Safari' in user_agent and 'Chrome' not in user_agent:
        browser_name = 'Safari'
    elif 'Edg' in user_agent:
        browser_name = 'Edge'
    else:
        browser_name = user_agent[:100]

    return browser_name[:255], os_name[:255], device_type


def home(request):
    return render(request, "edutrust_tuition_platform.html")


def book_demo_page(request):
    from TutionPlatform.views import home
    return home(request, initial_popup='free-trial')


@csrf_exempt
def book_demo_api(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

    try:
        try:
            data = json.loads(request.body.decode('utf-8')) if request.body else {}
        except Exception:
            data = request.POST

        student_data = data.get('student', {})
        tuition_data = data.get('tuition', {})
        tutor_data = data.get('tutor', {})
        address_data = tuition_data.get('address') or {}

        # Backend Validation
        student_name = (student_data.get('name') or data.get('student_name') or '').strip()
        student_mobile = (student_data.get('mobile') or data.get('student_mobile') or '').strip()
        student_email = (student_data.get('email') or data.get('student_email') or '').strip().lower()
        student_class = (student_data.get('class') or data.get('student_class') or '').strip()
        subject = (tuition_data.get('subject') or data.get('subject') or '').strip()
        tuition_mode = (tuition_data.get('mode') or data.get('tuition_mode') or 'Online / Home Demo').strip()

        errors = []
        if not student_name or len(student_name) < 2:
            errors.append('Student full name is required.')

        if not student_mobile or not re.match(r'^[6-9]\d{9}$', student_mobile):
            errors.append('A valid 10-digit mobile number is required.')

        if not student_email or not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', student_email):
            errors.append('A valid email address is required.')

        if not student_class:
            errors.append('Student class is required.')

        if not subject:
            errors.append('Subject is required.')

        if errors:
            return JsonResponse({
                'status': 'error',
                'message': errors[0],
                'errors': errors
            }, status=400)

        # Capture System Info
        ip = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        browser_name, os_name, device_type = parse_system_info(user_agent)

        # Resolve Selected Teacher Profile
        tutor_id_val = tutor_data.get('id') or tutor_data.get('tutor_id') or data.get('tutor_id') or data.get('teacher_id')
        teacher_obj = None
        if tutor_id_val:
            from TutionPlatform.models import TeacherProfile
            from django.db.models import Q
            try:
                clean_tid = int(str(tutor_id_val).strip())
                teacher_obj = TeacherProfile.objects.filter(pk=clean_tid).first()
            except Exception:
                pass
            if not teacher_obj:
                teacher_obj = TeacherProfile.objects.filter(teacher_id=str(tutor_id_val).strip()).first()

        # WEBSITE MODE BOOKING VALIDATION
        from TutionPlatform.website_mode import validate_booking_mode
        is_booking_valid, booking_err = validate_booking_mode(tuition_mode, teacher_obj=teacher_obj)
        if not is_booking_valid:
            return JsonResponse({'status': 'error', 'message': booking_err}, status=400)

        # Atomic Transaction for Booking, Log, and Notification
        with transaction.atomic():
            booking = FreeTrialBooking.objects.create(
                student_name=student_name,
                student_mobile=student_mobile,
                student_email=student_email,
                student_gender=student_data.get('gender') or data.get('student_gender'),
                student_class=student_class,
                board=student_data.get('board') or data.get('board'),
                subject=subject,
                
                tuition_mode=tuition_mode,
                preferred_demo_date=tuition_data.get('date') or data.get('preferred_demo_date') or None,
                preferred_time_slot=tuition_data.get('timeSlot') or data.get('preferred_time_slot'),
                number_of_demo_sessions=tuition_data.get('sessionsCount', 1),
                preferred_language=tuition_data.get('language') or data.get('preferred_language'),
                learning_goal=tuition_data.get('goal') or data.get('learning_goal'),
                additional_notes=tuition_data.get('notes') or data.get('additional_notes'),
                
                tutor_id=teacher_obj.teacher_id if teacher_obj else str(tutor_id_val or ''),
                tutor_name=teacher_obj.full_name if teacher_obj else (tutor_data.get('name') or data.get('tutor_name')),
                assigned_teacher=teacher_obj,
                tutor_photo=teacher_obj.profile_photo.url if (teacher_obj and teacher_obj.profile_photo) else (tutor_data.get('photo') or data.get('tutor_photo')),
                tutor_rating=str(teacher_obj.rating) if teacher_obj and hasattr(teacher_obj, 'rating') else (tutor_data.get('rating') or data.get('tutor_rating')),
                tutor_qualification=teacher_obj.qualification if teacher_obj else (tutor_data.get('qualification') or data.get('tutor_qualification')),
                tutor_experience=teacher_obj.experience if teacher_obj else (tutor_data.get('exp') or data.get('tutor_experience')),
                tutor_location=f"{teacher_obj.city}, {teacher_obj.state}" if teacher_obj else (tutor_data.get('location') or data.get('tutor_location')),
                tutor_mode=teacher_obj.tuition_mode if teacher_obj else (tutor_data.get('mode') or data.get('tutor_mode')),

                state=address_data.get('state') or data.get('state'),
                city=address_data.get('city') or data.get('city'),
                locality=address_data.get('locality') or data.get('locality'),
                landmark=address_data.get('landmark') or data.get('landmark'),
                complete_address=address_data.get('complete') or data.get('complete_address'),

                ip_address=ip,
                browser=browser_name,
                operating_system=os_name,
                device_type=device_type
            )

            # Activity Log
            ActivityLog.objects.create(
                activity_type='Demo Class Booked',
                user_name=student_name,
                user_role='Student',
                description=f"Free Trial Demo Booking ({booking.booking_id}) submitted by {student_name} for Class {student_class} ({subject}).",
                page_url=request.path,
                ip_address=ip,
                browser=browser_name,
                device_type=device_type
            )

            # Admin Notification
            AdminNotification.objects.create(
                title=f"New Demo Booking: {booking.booking_id}",
                message=f"Demo booked by {student_name} for {subject} (Class {student_class}).",
                category="demo_booking"
            )

        return JsonResponse({
            'status': 'success',
            'booking_id': booking.booking_id,
            'message': 'Free Trial Class Booking Successful!'
        })

    except Exception as e:
        logger.error("Booking API Exception: %s", str(e), exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': 'Booking request failed due to a server error. Please try again.'
        }, status=400)