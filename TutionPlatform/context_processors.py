from .models import (
    SystemSetting, Loader, StudentProfile, TeacherProfile, CourseEnrollment, PaymentTransaction,
    HomePageSection, HomePageContent, WebsiteForm, WebsiteNavigation, WebsiteFooterColumn
)
from django.db.models import Q

from .website_mode import (
    get_website_mode, is_home_tuition_mode, is_online_tuition_mode,
    is_full_lms_mode, feature_enabled, get_feature_matrix
)
from .why_choose_config import get_why_choose_config
from .footer_config import get_active_footer_config

def global_branding_context(request):
    """
    Injects platform_logo_url, theme colors, active loader, website contact info, 
    homepage CMS settings, navigation menus, social links, authenticated student profile details,
    and global website mode feature controller flags.
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

    # Fetch Homepage Key-Value Settings dictionary
    homepage_settings = {}
    try:
        hp_objs = SystemSetting.objects.filter(category='homepage')
        for h in hp_objs:
            homepage_settings[h.key] = h.value
    except Exception:
        pass

    website_mode = get_website_mode()
    features_matrix = get_feature_matrix()

    # Fetch Contact Details
    website_email = homepage_settings.get('contact_primary_email') or SystemSetting.objects.filter(key='contact_email').values_list('value', flat=True).first() or 'support@edutrust.com'
    website_contact_phone = homepage_settings.get('contact_primary_phone') or SystemSetting.objects.filter(key='contact_phone').values_list('value', flat=True).first() or '+91 9876543210'

    # Fetch Social Media Links
    social_whatsapp = homepage_settings.get('social_whatsapp_url') if (homepage_settings.get('social_whatsapp_enabled', 'true') == 'true') else ''
    social_facebook = homepage_settings.get('social_facebook_url') if (homepage_settings.get('social_facebook_enabled', 'true') == 'true') else ''
    social_instagram = homepage_settings.get('social_instagram_url') if (homepage_settings.get('social_instagram_enabled', 'true') == 'true') else ''
    social_x = homepage_settings.get('social_twitter_url') if (homepage_settings.get('social_twitter_enabled', 'true') == 'true') else 'https://x.com/edutrust'
    social_youtube = homepage_settings.get('social_youtube_url') if (homepage_settings.get('social_youtube_enabled', 'true') == 'true') else ''
    social_linkedin = homepage_settings.get('social_linkedin_url') if (homepage_settings.get('social_linkedin_enabled', 'true') == 'true') else ''

    # Fetch Homepage Sections & Content
    active_sections_map = {}
    homepage_sections_list = []
    try:
        sec_qs = HomePageSection.objects.filter(is_enabled=True).order_by('display_order', 'id')
        for s in sec_qs:
            # Mode restriction check for sections
            if website_mode == 'home_tuition' and s.section_key in ['courses', 'live_classes', 'lms_features', 'online_tests']:
                continue
            elif website_mode == 'online_tuition' and s.section_key in ['home_tutors_only', 'courses', 'lms_features']:
                continue

            active_sections_map[s.section_key] = True
            homepage_sections_list.append({
                'key': s.section_key,
                'title': s.title,
                'subtitle': s.subtitle
            })
    except Exception:
        pass

    homepage_content_dict = {}
    try:
        cnt_qs = HomePageContent.objects.filter(is_enabled=True).order_by('display_order', 'id')
        for c in cnt_qs:
            if c.section_key not in homepage_content_dict:
                homepage_content_dict[c.section_key] = []
            homepage_content_dict[c.section_key].append(c)
    except Exception:
        pass

    # Fetch Navigation Items
    homepage_nav_header = []
    homepage_nav_footer = []
    try:
        nav_qs = WebsiteNavigation.objects.filter(is_enabled=True).order_by('display_order', 'id')
        for n in nav_qs:
            # Mode restriction check
            if n.mode_restriction and n.mode_restriction != 'all':
                if website_mode == 'home_tuition' and n.mode_restriction in ['lms', 'full_lms', 'home_online', 'online_tuition']:
                    continue
                elif website_mode == 'online_tuition' and n.mode_restriction in ['lms', 'full_lms', 'home_tuition']:
                    continue

            if n.position in ['header', 'both']:
                homepage_nav_header.append(n)
            if n.position in ['footer', 'both']:
                homepage_nav_footer.append(n)
    except Exception:
        pass

    # Fetch Footer Columns
    homepage_footer_columns = []
    try:
        fcols = WebsiteFooterColumn.objects.filter(is_enabled=True).order_by('display_order', 'id')
        for col in fcols:
            links = col.links.filter(is_enabled=True).order_by('display_order', 'id')
            homepage_footer_columns.append({
                'title': col.title,
                'links': links
            })
    except Exception:
        pass

    # Authenticated Teacher & Student Resolution & Batch Access Check
    logged_in_student = None
    logged_in_teacher = None
    has_valid_batch = False
    student_completion_percent = 0

    try:
        user_role = str(request.session.get('user_role') or request.session.get('role') or '').lower()
        session_email = (request.session.get('email') or '').strip().lower()
        session_user_id = request.session.get('user_id')
        session_teacher_id = request.session.get('teacher_id')

        # 1. Check if user is logged in as Teacher
        if user_role in ['teacher', 'tutor'] or session_teacher_id:
            tp = None
            if session_teacher_id:
                tp = TeacherProfile.objects.filter(teacher_id=session_teacher_id).first()
            if not tp and session_user_id:
                if str(session_user_id).startswith('TUT-'):
                    tp = TeacherProfile.objects.filter(teacher_id=session_user_id).first()
                elif str(session_user_id).isdigit():
                    tp = TeacherProfile.objects.filter(id=int(session_user_id)).first()
            if not tp and session_email:
                tp = TeacherProfile.objects.filter(email__iexact=session_email).first()
            if tp:
                logged_in_teacher = tp

        # 2. Check if user is logged in as Student
        if not logged_in_teacher and (user_role == 'student' or session_email or session_user_id):
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
        logged_in_teacher = None
        logged_in_student = None
        has_valid_batch = False
        student_completion_percent = 0

    # Active Footer Configuration (CMS)
    footer_config, footer_disabled_on_this_page = get_active_footer_config(getattr(request, 'path', '/'))

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
        'social_youtube': social_youtube,
        'social_linkedin': social_linkedin,
        'homepage_settings': homepage_settings,
        'system_settings': homepage_settings,
        'why_choose': get_why_choose_config(),
        'website_mode': website_mode,
        'is_home_tuition_mode': is_home_tuition_mode(),
        'is_online_tuition_mode': is_online_tuition_mode(),
        'is_full_lms_mode': is_full_lms_mode(),
        'features_enabled': features_matrix,
        'active_sections_map': active_sections_map,
        'homepage_sections_list': homepage_sections_list,
        'homepage_content_dict': homepage_content_dict,
        'homepage_nav_header': homepage_nav_header,
        'homepage_nav_footer': homepage_nav_footer,
        'homepage_footer_columns': homepage_footer_columns,
        'footer_config': footer_config,
        'footer_disabled_on_this_page': footer_disabled_on_this_page,
        'logged_in_teacher': logged_in_teacher,
        'logged_in_student': logged_in_student,
        'has_valid_batch': has_valid_batch,
        'student_completion_percent': student_completion_percent,
        'current_path': request.path,
    }

