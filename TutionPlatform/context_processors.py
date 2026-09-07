from .models import SystemSetting, Loader, StudentProfile, CourseEnrollment, PaymentTransaction
from django.db.models import Q

def global_branding_context(request):
    """
    Injects platform_logo_url, theme colors, active loader, website contact info, 
    and authenticated student profile details globally into ALL Django templates.
    """
    try:
        logo_setting = SystemSetting.objects.filter(key='logo', category='branding').first()
        logo_url = logo_setting.value if (logo_setting and logo_setting.value) else ''
    except Exception:
        logo_url = ''
        
    try:
        primary_setting = SystemSetting.objects.filter(key='primary_color', category='branding').first()
        primary_color = primary_setting.value if primary_setting else '#2563eb'
    except Exception:
        primary_color = '#2563eb'

    try:
        secondary_setting = SystemSetting.objects.filter(key='secondary_color', category='branding').first()
        secondary_color = secondary_setting.value if secondary_setting else '#7c3aed'
    except Exception:
        secondary_color = '#7c3aed'

    try:
        active_loader = Loader.objects.filter(is_active=True, is_enabled=True).first()
    except Exception:
        active_loader = None

    # Fetch Website Contact Settings (from SystemSetting if available)
    try:
        email_obj = SystemSetting.objects.filter(key='contact_email').first()
        website_email = email_obj.value if (email_obj and email_obj.value) else 'support@edutrust.com'
    except Exception:
        website_email = 'support@edutrust.com'

    try:
        phone_obj = SystemSetting.objects.filter(key='contact_phone').first()
        website_contact_phone = phone_obj.value if (phone_obj and phone_obj.value) else '+91 9876543210'
    except Exception:
        website_contact_phone = '+91 9876543210'

    # Fetch Social Media Settings
    try:
        wa_obj = SystemSetting.objects.filter(key='whatsapp_url').first()
        social_whatsapp = wa_obj.value if (wa_obj and wa_obj.value) else 'https://wa.me/919876543210'
    except Exception:
        social_whatsapp = 'https://wa.me/919876543210'

    try:
        fb_obj = SystemSetting.objects.filter(key='facebook_url').first()
        social_facebook = fb_obj.value if (fb_obj and fb_obj.value) else 'https://facebook.com/edutrust'
    except Exception:
        social_facebook = 'https://facebook.com/edutrust'

    try:
        insta_obj = SystemSetting.objects.filter(key='instagram_url').first()
        social_instagram = insta_obj.value if (insta_obj and insta_obj.value) else 'https://instagram.com/edutrust'
    except Exception:
        social_instagram = 'https://instagram.com/edutrust'

    try:
        x_obj = SystemSetting.objects.filter(key='twitter_url').first()
        social_x = x_obj.value if (x_obj and x_obj.value) else 'https://x.com/edutrust'
    except Exception:
        social_x = 'https://x.com/edutrust'

    # Authenticated Student Resolution & Batch Access Check
    logged_in_student = None
    has_valid_batch = False
    student_completion_percent = 0

    try:
        user_role = str(request.session.get('user_role') or request.session.get('role') or '').lower()
        session_email = (request.session.get('email') or '').strip().lower()
        session_user_id = request.session.get('user_id')

        # Check if user is logged in as Student
        if user_role == 'student' or session_email or session_user_id:
            sp = None
            if session_email:
                sp = StudentProfile.objects.filter(email__iexact=session_email).first()
            if not sp and session_user_id:
                if str(session_user_id).isdigit():
                    sp = StudentProfile.objects.filter(Q(student_id=session_user_id) | Q(id=int(session_user_id))).first()
                else:
                    sp = StudentProfile.objects.filter(student_id=session_user_id).first()
            if not sp and hasattr(request, 'user') and getattr(request.user, 'is_authenticated', False) and request.user.email:
                sp = StudentProfile.objects.filter(email__iexact=request.user.email).first()

            if sp:
                logged_in_student = sp

                # Calculate Profile Completion Percentage
                fields_to_check = [
                    sp.full_name, sp.email, sp.mobile, sp.gender, sp.student_class,
                    sp.board, sp.city, sp.state, sp.dob, sp.father_name, sp.mother_name,
                    sp.address, sp.pincode, sp.school_name, (sp.profile_photo or sp.photo_url)
                ]
                filled_count = sum(1 for f in fields_to_check if f)
                student_completion_percent = min(100, int((filled_count / len(fields_to_check)) * 100))

                # Check Batch Purchase / Enrollment Status
                has_enrollment = CourseEnrollment.objects.filter(
                    student=sp,
                    payment_status__iexact='Success'
                ).exists()

                if not has_enrollment:
                    has_payment = PaymentTransaction.objects.filter(
                        status__iexact='Success'
                    ).filter(
                        Q(student_email__iexact=sp.email) | Q(student_id_code=sp.student_id)
                    ).exists()
                    if has_payment:
                        has_enrollment = True

                has_valid_batch = has_enrollment
    except Exception:
        logged_in_student = None
        has_valid_batch = False
        student_completion_percent = 0

    return {
        'platform_logo_url': logo_url,
        'platform_primary_color': primary_color,
        'platform_secondary_color': secondary_color,
        'platform_active_loader': active_loader,
        'active_loader': active_loader,
        'loader_enabled': bool(active_loader and active_loader.show_on_website),
        'website_email': website_email,
        'website_contact_phone': website_contact_phone,
        'social_whatsapp': social_whatsapp,
        'social_facebook': social_facebook,
        'social_instagram': social_instagram,
        'social_x': social_x,
        'logged_in_student': logged_in_student,
        'has_valid_batch': has_valid_batch,
        'student_completion_percent': student_completion_percent,
        'current_path': request.path,
    }

