# -*- coding: utf-8 -*-
"""
Centralized Global Website Mode Feature Controller for EduTrust
Provides:
- Single source of truth for the current website mode (home_tuition, online_tuition, full_lms)
- Centralized feature matrix
- Helper functions: get_website_mode(), is_home_tuition_mode(), is_online_tuition_mode(), is_full_lms_mode()
- Feature check function: feature_enabled(feature_name)
- View decorator: require_website_feature(feature_name)
- Direct URL access validation
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q

ALLOWED_WEBSITE_MODES = ['home_tuition', 'online_tuition', 'full_lms']
DEFAULT_WEBSITE_MODE = 'home_tuition'

FEATURE_MATRIX = {
    'home_tuition': {
        'home_tuition': True,
        'online_tuition': False,
        'courses': False,
        'live_classes': False,
        'recorded_classes': False,
        'exams': False,
        'assignments': False,
        'certificates': False,
        'study_material': False,
        'lms_progress': False,
        'lms_dashboard': False,
        'local_tutor_search': True,
        'online_tutor_search': False,
        'home_booking': True,
        'online_booking': False,
        'tutor_registration': True,
        'free_trial': True,
        'tuition_jobs': True,
    },
    'online_tuition': {
        'home_tuition': False,
        'online_tuition': True,
        'courses': False,
        'live_classes': True,
        'recorded_classes': False,
        'exams': False,
        'assignments': False,
        'certificates': False,
        'study_material': False,
        'lms_progress': False,
        'lms_dashboard': False,
        'local_tutor_search': False,
        'online_tutor_search': True,
        'home_booking': False,
        'online_booking': True,
        'tutor_registration': True,
        'free_trial': True,
        'tuition_jobs': True,
    },
    'full_lms': {
        'home_tuition': True,
        'online_tuition': True,
        'courses': True,
        'live_classes': True,
        'recorded_classes': True,
        'exams': True,
        'assignments': True,
        'certificates': True,
        'study_material': True,
        'lms_progress': True,
        'lms_dashboard': True,
        'local_tutor_search': True,
        'online_tutor_search': True,
        'home_booking': True,
        'online_booking': True,
        'tutor_registration': True,
        'free_trial': True,
        'tuition_jobs': True,
    }
}


import time

_WEBSITE_MODE_CACHE = None
_WEBSITE_MODE_CACHE_TIME = 0

def get_website_mode():
    """
    Returns the normalized current active website mode.
    One of: 'home_tuition', 'online_tuition', 'full_lms'
    Fast cached implementation (60-second TTL).
    """
    global _WEBSITE_MODE_CACHE, _WEBSITE_MODE_CACHE_TIME
    now = time.time()
    if _WEBSITE_MODE_CACHE is not None and (now - _WEBSITE_MODE_CACHE_TIME < 60):
        return _WEBSITE_MODE_CACHE

    try:
        from .models import SystemSetting
        mode_setting = SystemSetting.objects.filter(key='website_mode', category='homepage').first()
        raw_val = mode_setting.value.strip() if mode_setting and mode_setting.value else DEFAULT_WEBSITE_MODE
    except Exception:
        raw_val = DEFAULT_WEBSITE_MODE

    # Normalize legacy database values
    if raw_val in ['home_tuition_only', 'home_tuition']:
        res = 'home_tuition'
    elif raw_val in ['home_online', 'online_tuition']:
        res = 'online_tuition'
    elif raw_val == 'full_lms':
        res = 'full_lms'
    else:
        res = DEFAULT_WEBSITE_MODE

    _WEBSITE_MODE_CACHE = res
    _WEBSITE_MODE_CACHE_TIME = now
    return res


def is_home_tuition_mode():
    return get_website_mode() == 'home_tuition'


def is_online_tuition_mode():
    return get_website_mode() == 'online_tuition'


def is_full_lms_mode():
    return get_website_mode() == 'full_lms'


def feature_enabled(feature_name, mode=None):
    """
    Checks if a specific feature is enabled for the current or given website mode.
    """
    active_mode = mode or get_website_mode()
    mode_features = FEATURE_MATRIX.get(active_mode, FEATURE_MATRIX[DEFAULT_WEBSITE_MODE])
    return mode_features.get(feature_name, False)


def get_feature_matrix(mode=None):
    """
    Returns the entire feature map for the active or given website mode.
    """
    active_mode = mode or get_website_mode()
    return FEATURE_MATRIX.get(active_mode, FEATURE_MATRIX[DEFAULT_WEBSITE_MODE]).copy()


def is_admin_or_staff(request):
    """
    Check if the current request user is a superadmin, staff, or admin role.
    Admin users bypass public website mode restrictions.
    """
    if not request:
        return False
    user_role = str(request.session.get('user_role') or request.session.get('role') or '').lower()
    if user_role in ['admin', 'superadmin', 'subadmin', 'staff']:
        return True
    user = getattr(request, 'user', None)
    if user and getattr(user, 'is_authenticated', False) and (getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False)):
        return True
    return False


def get_allowed_teaching_modes(mode=None):
    """
    Returns list of allowed teaching modes for teacher registration & forms.
    - home_tuition: ['Home Tuition']
    - online_tuition: ['Online Tuition']
    - full_lms: ['Home Tuition', 'Online Tuition', 'Hybrid']
    """
    active_mode = mode or get_website_mode()
    if active_mode == 'home_tuition':
        return ['Home Tuition']
    elif active_mode == 'online_tuition':
        return ['Online Tuition']
    else:
        return ['Home Tuition', 'Online Tuition', 'Hybrid']


def is_teacher_compatible_with_mode(teacher_obj_or_mode, mode=None):
    """
    Checks if a teacher or teaching mode string is compatible with the given or active website mode.
    """
    active_mode = mode or get_website_mode()
    if active_mode == 'full_lms':
        return True

    t_mode = ''
    if hasattr(teacher_obj_or_mode, 'tuition_mode'):
        t_mode = getattr(teacher_obj_or_mode, 'tuition_mode', '') or ''
    elif isinstance(teacher_obj_or_mode, str):
        t_mode = teacher_obj_or_mode
    else:
        return False

    t_mode_clean = t_mode.strip().lower()

    if active_mode == 'home_tuition':
        # Must be Home Tuition ONLY. Exclude Online, Hybrid, All, Both, Home & Online
        if 'online' in t_mode_clean or 'hybrid' in t_mode_clean or 'all' in t_mode_clean or '&' in t_mode_clean or 'both' in t_mode_clean:
            return False
        return 'home' in t_mode_clean

    elif active_mode == 'online_tuition':
        # Must be Online Tuition ONLY. Exclude Home, Hybrid, All, Both, Home & Online
        if 'home' in t_mode_clean or 'hybrid' in t_mode_clean or 'all' in t_mode_clean or '&' in t_mode_clean or 'both' in t_mode_clean:
            return False
        return 'online' in t_mode_clean

    return True


def filter_teachers_query(queryset, mode=None, allow_admin_bypass=True, request=None):
    """
    Filters a TeacherProfile queryset based on the active website mode.
    Ensures that only mode-compatible tutors are returned from public queries.
    """
    if allow_admin_bypass and request and is_admin_or_staff(request):
        return queryset

    active_mode = mode or get_website_mode()

    if active_mode == 'home_tuition':
        return queryset.filter(
            Q(tuition_mode__iexact='Home Tuition') | Q(tuition_mode__iexact='Home')
        ).exclude(
            Q(tuition_mode__icontains='Online') | Q(tuition_mode__icontains='Hybrid') | Q(tuition_mode__icontains='All') | Q(tuition_mode__icontains='&') | Q(tuition_mode__icontains='Both')
        )

    elif active_mode == 'online_tuition':
        return queryset.filter(
            Q(tuition_mode__iexact='Online Tuition') | Q(tuition_mode__iexact='Online')
        ).exclude(
            Q(tuition_mode__icontains='Home') | Q(tuition_mode__icontains='Hybrid') | Q(tuition_mode__icontains='All') | Q(tuition_mode__icontains='&') | Q(tuition_mode__icontains='Both')
        )

    # In full_lms mode, return all tutors
    return queryset


def validate_teacher_registration_mode(submitted_mode, mode=None):
    """
    Validates a submitted teaching mode during teacher registration.
    Returns (is_valid: bool, normalized_mode: str, error_message: str)
    """
    active_mode = mode or get_website_mode()
    mode_str = (submitted_mode or '').strip()

    if active_mode == 'home_tuition':
        if mode_str.lower() in ['home tuition', 'home']:
            return True, 'Home Tuition', ''
        return False, '', 'Only Home Tuition registration is allowed in the current website mode.'

    elif active_mode == 'online_tuition':
        if mode_str.lower() in ['online tuition', 'online']:
            return True, 'Online Tuition', ''
        return False, '', 'Only Online Tuition registration is allowed in the current website mode.'

    else: # full_lms
        if mode_str.lower() in ['home tuition', 'home']:
            return True, 'Home Tuition', ''
        elif mode_str.lower() in ['online tuition', 'online']:
            return True, 'Online Tuition', ''
        elif mode_str.lower() in ['hybrid', 'all', 'home & online', 'home / online', 'home & online tuition']:
            return True, 'Hybrid', ''
        elif mode_str:
            return True, mode_str, ''
        return False, '', 'Please select a valid teaching mode.'


def validate_booking_mode(submitted_mode, teacher_obj=None, mode=None):
    """
    Validates tuition/demo booking mode and selected teacher against active website mode.
    Returns (is_valid: bool, error_message: str)
    """
    active_mode = mode or get_website_mode()
    mode_str = (submitted_mode or '').strip().lower()

    if active_mode == 'home_tuition':
        if 'online' in mode_str:
            return False, 'Online tuition booking is not available in Home Tuition mode.'
        if teacher_obj and not is_teacher_compatible_with_mode(teacher_obj, 'home_tuition'):
            return False, 'The selected tutor is not available for Home Tuition bookings under the current website mode.'

    elif active_mode == 'online_tuition':
        if 'home' in mode_str:
            return False, 'Home tuition booking is not available in Online Tuition mode.'
        if teacher_obj and not is_teacher_compatible_with_mode(teacher_obj, 'online_tuition'):
            return False, 'The selected tutor is not available for Online Tuition bookings under the current website mode.'

    return True, ''


def require_website_feature(feature_name, redirect_url='/'):
    """
    Decorator to protect public routes from being accessed directly via URL
    when the corresponding feature is disabled in the active website mode.
    Staff/Admin users are NEVER blocked.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if is_admin_or_staff(request):
                return view_func(request, *args, **kwargs)

            if not feature_enabled(feature_name):
                # If API call, return JSON response
                if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.path.startswith('/api/'):
                    return JsonResponse({
                        'status': 'error',
                        'error': f'The requested feature ({feature_name}) is not available in the current website mode.'
                    }, status=403)

                # Flash message and redirect gracefully
                mode_title = get_website_mode().replace('_', ' ').title()
                messages.warning(
                    request,
                    f'This section is not available in {mode_title} mode.'
                )
                return redirect(redirect_url)

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
