from django.utils import timezone
from .models import ActivityLog, VisitorTracker

class ActivityLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        path = request.path
        # Ignore static, media, admin assets
        if path.startswith('/static/') or path.startswith('/media/') or path.endswith('.png') or path.endswith('.jpg') or path.endswith('.ico') or path.endswith('.css') or path.endswith('.js'):
            return response

        try:
            ip = request.META.get('HTTP_X_FORWARDED_FOR')
            if ip:
                ip = ip.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR', '127.0.0.1')

            user_agent = request.META.get('HTTP_USER_AGENT', '')
            device_type = 'Mobile' if 'Mobile' in user_agent or 'Android' in user_agent or 'iPhone' in user_agent else 'Desktop'
            
            browser = 'Web Browser'
            if 'Chrome' in user_agent:
                browser = 'Chrome'
            elif 'Firefox' in user_agent:
                browser = 'Firefox'
            elif 'Safari' in user_agent and 'Chrome' not in user_agent:
                browser = 'Safari'
            elif 'Edg' in user_agent:
                browser = 'Edge'

            today = timezone.now().date()
            
            # Log Visitor
            VisitorTracker.objects.update_or_create(
                ip_address=ip,
                page_visited=path,
                visit_date=today,
                defaults={'user_agent': user_agent, 'last_seen': timezone.now()}
            )

            # Log Page Visit for key pages if GET
            if request.method == 'GET' and not path.startswith('/api/'):
                page_names = {
                    '/': 'Home Page',
                    '/edutrust_tuition_platform.html': 'Home Page',
                    '/findtutor.html': 'Find Tutor Page',
                    '/find-tutor/': 'Find Tutor Page',
                    '/teacher-registration.html': 'Teacher Registration Page',
                    '/teacher-registration/': 'Teacher Registration Page',
                    '/registration.html': 'Student Registration Page',
                    '/login.html': 'Login Page',
                    '/book-demo/': 'Book Demo Page',
                    '/book_demo.html': 'Book Demo Page',
                    '/studymaterial.html': 'Study Material Page',
                    '/admin.html': 'Super Admin Dashboard',
                    '/custom-admin/': 'Super Admin Dashboard',
                }
                
                if path in page_names:
                    ActivityLog.objects.create(
                        activity_type='Page Visit',
                        user_name='Visitor',
                        user_role='Visitor',
                        description=f"Visited {page_names[path]} ({path})",
                        page_url=path,
                        ip_address=ip,
                        browser=browser,
                        device_type=device_type
                    )

        except Exception as e:
            # Prevent middleware errors from affecting user requests
            pass

        return response


class SuperAdminAccessMiddleware:
    """
    Centralized middleware enforcing strict Super Admin role authentication & session security.
    Protects all /admin/* and /api/admin/* routes.
    """
    EXEMPT_PATHS = [
        '/admin/login/',
        '/admin/verify-otp/',
        '/admin/forgot-password/',
        '/admin/reset-password/',
        '/admin/logout/',
        '/api/admin/auth/login/',
        '/api/admin/auth/verify-otp/',
        '/api/admin/auth/resend-otp/',
        '/api/admin/auth/forgot-password/',
        '/api/admin/auth/reset-password/',
        '/api/admin/auth/recovery/send-otp/',
        '/api/admin/auth/recovery/verify-otp/',
        '/api/admin/auth/recovery/change-password/',
        '/api/admin/auth/recovery/change-identity/',
        '/api/admin/auth/recovery/update-account/',
        '/api/admin/communication/stats/',
        '/api/admin/communication/conversations/',
        '/api/admin/communication/thread/',
        '/api/admin/communication/messages/',
        '/api/admin/communication/send/',
        '/api/admin/communication/broadcast/',
        '/api/admin/communication/notices/',
        '/api/admin/communication/support/',
        '/api/admin/communication/user-drawer/',
        '/api/admin/communication/toggle-star/',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # Ignore static, media assets
        if path.startswith('/static/') or path.startswith('/media/'):
            return self.get_response(request)

        # Check if route is an admin protected route
        is_admin_route = path.startswith('/admin/') or path.startswith('/api/admin/')

        if is_admin_route:
            # Direct root admin path directly to /admin/login/
            if path in ('/admin/', '/admin'):
                from django.shortcuts import redirect
                return redirect('/admin/login/')

            # Check if path is exempt from authentication
            if any(path == exempt or path.startswith(exempt) for exempt in self.EXEMPT_PATHS):
                return self.get_response(request)

            # Enforce Server-Side Super Admin Role Verification
            user = getattr(request, 'user', None)
            is_authenticated = user and user.is_authenticated
            is_super_admin = is_authenticated and (user.is_superuser or user.is_staff or request.session.get('super_admin_verified') is True)
            is_active = is_authenticated and user.is_active

            # Idle session timeout check (30 minutes = 1800 seconds)
            if is_super_admin:
                last_activity = request.session.get('admin_last_activity')
                now_ts = int(timezone.now().timestamp())
                if last_activity and (now_ts - last_activity > 1800):
                    # Invalidate session due to idle timeout
                    request.session.flush()
                    if path.startswith('/api/'):
                        from django.http import JsonResponse
                        return JsonResponse({'status': 'error', 'message': 'Session expired due to inactivity. Please log in again.'}, status=401)
                    from django.shortcuts import redirect
                    if path in ('/admin/', '/admin', '/admin/login/', '/admin/login'):
                        return redirect('/admin/login/?expired=1')
                    import urllib.parse
                    return redirect(f'/admin/login/?next={urllib.parse.quote(path)}&expired=1')
                
                # Update last activity timestamp
                request.session['admin_last_activity'] = now_ts

            if not is_authenticated or not is_super_admin or not is_active:
                if path.startswith('/api/'):
                    from django.http import JsonResponse
                    return JsonResponse({'status': 'error', 'message': 'Super Admin authorization required. Access denied.'}, status=401)
                
                from django.shortcuts import redirect
                if path in ('/admin/', '/admin', '/admin/login/', '/admin/login'):
                    return redirect('/admin/login/')
                import urllib.parse
                login_target = f'/admin/login/?next={urllib.parse.quote(path)}'
                return redirect(login_target)

        return self.get_response(request)
