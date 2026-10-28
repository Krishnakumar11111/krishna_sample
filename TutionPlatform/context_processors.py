from .models import (
    SystemSetting, Loader, StudentProfile, TeacherProfile, CourseEnrollment, PaymentTransaction,
    HomePageSection, HomePageContent, WebsiteForm, WebsiteNavigation, WebsiteFooterColumn
)
from django.db.models import Q
import time

from .website_mode import (
    get_website_mode, is_home_tuition_mode, is_online_tuition_mode,
    is_full_lms_mode, feature_enabled, get_feature_matrix
)
from .why_choose_config import get_why_choose_config
from .footer_config import get_active_footer_config

# High-Performance In-Memory Caching (60-second TTL to eliminate redundant WAN queries)
_BRANDING_FAST_CACHE = {}
_BRANDING_FAST_CACHE_TIME = 0

_FULL_PAGE_CACHE = {}
_FULL_PAGE_CACHE_TIME = 0

def _get_minimal_branding_context():
    global _BRANDING_FAST_CACHE, _BRANDING_FAST_CACHE_TIME
    now = time.time()
    if _BRANDING_FAST_CACHE and (now - _BRANDING_FAST_CACHE_TIME < 60):
        return dict(_BRANDING_FAST_CACHE)

    try:
        brand_map = {s.key: s.value for s in SystemSetting.objects.filter(category='branding', key__in=['logo', 'primary_color', 'secondary_color'])}
        logo_url = brand_map.get('logo', '')
        primary_color = brand_map.get('primary_color', '#2563eb')
        secondary_color = brand_map.get('secondary_color', '#7c3aed')
    except Exception:
        logo_url = ''
        primary_color = '#2563eb'
        secondary_color = '#7c3aed'

    try:
        active_loader = Loader.objects.filter(is_active=True, is_enabled=True).first()
    except Exception:
        active_loader = None

    _BRANDING_FAST_CACHE = {
        'platform_logo_url': logo_url,
        'platform_primary_color': primary_color,
        'platform_secondary_color': secondary_color,
        'platform_active_loader': active_loader,
        'active_loader': active_loader,
        'loader_enabled': bool(active_loader and active_loader.show_on_website),
    }
    _BRANDING_FAST_CACHE_TIME = now
    return dict(_BRANDING_FAST_CACHE)

def global_branding_context(request):
    """
    Injects platform_logo_url, theme colors, active loader, website contact info, 
    homepage CMS settings, navigation menus, social links, authenticated student profile details,
    and global website mode feature controller flags.
    High-performance cached execution for sub-second response times.
    """
    # 1. Ultra-fast path for AJAX requests and all Admin panel routes
    path = getattr(request, 'path', '/')
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json'
    is_admin = path.startswith('/admin') or path.startswith('/api/admin')
    if is_ajax or is_admin:
        ctx = _get_minimal_branding_context()
        ctx['current_path'] = path
        return ctx

    # 2. Check full-page cache for static branding, CMS settings and footer configuration
    global _FULL_PAGE_CACHE, _FULL_PAGE_CACHE_TIME
    now = time.time()

    if _FULL_PAGE_CACHE and (now - _FULL_PAGE_CACHE_TIME < 60):
        cached_copy = dict(_FULL_PAGE_CACHE)
    else:
        try:
            brand_map = {s.key: s.value for s in SystemSetting.objects.filter(category='branding', key__in=['logo', 'primary_color', 'secondary_color'])}
            logo_url = brand_map.get('logo', '')
            primary_color = brand_map.get('primary_color', '#2563eb')
            secondary_color = brand_map.get('secondary_color', '#7c3aed')
        except Exception:
            logo_url = ''
            primary_color = '#2563eb'
            secondary_color = '#7c3aed'

        try:
            active_loader = Loader.objects.filter(is_active=True, is_enabled=True).first()
        except Exception:
            active_loader = None

        homepage_settings = {}
        try:
            hp_objs = SystemSetting.objects.filter(category='homepage')
            for h in hp_objs:
                homepage_settings[h.key] = h.value
        except Exception:
            pass

        website_mode = get_website_mode()
        features_matrix = get_feature_matrix()

        website_email = homepage_settings.get('contact_primary_email') or 'support@edutrust.com'
        website_contact_phone = homepage_settings.get('contact_primary_phone') or '+91 9876543210'

        social_whatsapp = homepage_settings.get('social_whatsapp_url') if (homepage_settings.get('social_whatsapp_enabled', 'true') == 'true') else ''
        social_facebook = homepage_settings.get('social_facebook_url') if (homepage_settings.get('social_facebook_enabled', 'true') == 'true') else ''
        social_instagram = homepage_settings.get('social_instagram_url') if (homepage_settings.get('social_instagram_enabled', 'true') == 'true') else ''
        social_x = homepage_settings.get('social_twitter_url') if (homepage_settings.get('social_twitter_enabled', 'true') == 'true') else 'https://x.com/edutrust'
        social_youtube = homepage_settings.get('social_youtube_url') if (homepage_settings.get('social_youtube_enabled', 'true') == 'true') else ''
        social_linkedin = homepage_settings.get('social_linkedin_url') if (homepage_settings.get('social_linkedin_enabled', 'true') == 'true') else ''

        active_sections_map = {}
        homepage_sections_list = []
        try:
            sec_qs = HomePageSection.objects.filter(is_enabled=True).order_by('display_order', 'id')
            for s in sec_qs:
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

        homepage_nav_header = []
        homepage_nav_footer = []
        try:
            nav_qs = WebsiteNavigation.objects.filter(is_enabled=True).order_by('display_order', 'id')
            for n in nav_qs:
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

        homepage_footer_columns = []
        try:
            fcols = list(WebsiteFooterColumn.objects.filter(is_enabled=True).prefetch_related('links').order_by('display_order', 'id'))
            for col in fcols:
                col_links = [l for l in col.links.all() if l.is_enabled]
                col_links.sort(key=lambda x: (x.display_order, x.id))
                homepage_footer_columns.append({
                    'title': col.title,
                    'links': col_links
                })
        except Exception:
            pass

        try:
            why_choose = get_why_choose_config()
        except Exception:
            why_choose = {}

        _FULL_PAGE_CACHE = {
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
            'why_choose': why_choose,
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
        }
        _FULL_PAGE_CACHE_TIME = now
        cached_copy = dict(_FULL_PAGE_CACHE)

    # 3. Dynamic Request-Specific Context (Student / Teacher auth & Footer per path)
    footer_config, footer_disabled_on_this_page = get_active_footer_config(getattr(request, 'path', '/'))
    cached_copy['footer_config'] = footer_config
    cached_copy['footer_disabled_on_this_page'] = footer_disabled_on_this_page
    cached_copy['current_path'] = getattr(request, 'path', '/')

    # Authenticated Teacher & Student Resolution (Only if user has relevant session keys)
    logged_in_student = None
    logged_in_teacher = None
    has_valid_batch = False
    student_completion_percent = 0

    try:
        user_role = str(request.session.get('user_role') or request.session.get('role') or '').lower()
        session_email = (request.session.get('email') or '').strip().lower()
        session_user_id = request.session.get('user_id')
        session_teacher_id = request.session.get('teacher_id')

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

        if not logged_in_teacher and (user_role == 'student' or (session_email and not getattr(request.user, 'is_staff', False))):
            sp = None
            if session_email:
                sp = StudentProfile.objects.filter(email__iexact=session_email).first()
            if not sp and session_user_id:
                if str(session_user_id).isdigit():
                    sp = StudentProfile.objects.filter(Q(student_id=session_user_id) | Q(id=int(session_user_id))).first()
                else:
                    sp = StudentProfile.objects.filter(student_id=session_user_id).first()

            if sp:
                logged_in_student = sp
                fields_to_check = [
                    sp.full_name, sp.email, sp.mobile, sp.gender, sp.student_class,
                    sp.board, sp.city, sp.state, sp.dob, sp.father_name, sp.mother_name,
                    sp.address, sp.pincode, sp.school_name, (sp.profile_photo or sp.photo_url)
                ]
                filled_count = sum(1 for f in fields_to_check if f)
                student_completion_percent = min(100, int((filled_count / len(fields_to_check)) * 100))

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
        pass

    cached_copy['logged_in_teacher'] = logged_in_teacher
    cached_copy['logged_in_student'] = logged_in_student
    cached_copy['has_valid_batch'] = has_valid_batch
    cached_copy['student_completion_percent'] = student_completion_percent
    return cached_copy

