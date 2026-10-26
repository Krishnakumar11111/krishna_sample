import os, random, hashlib, datetime, json, re
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import update_session_auth_hash
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q

from .models import AdminOTP, AdminSecurityLog

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '127.0.0.1')

def log_admin_security_event(user, event, request, status='SUCCESS', description=''):
    try:
        ip = get_client_ip(request)
        ua = request.META.get('HTTP_USER_AGENT', '')
        AdminSecurityLog.objects.create(
            user=user if user and user.is_authenticated else (user if isinstance(user, User) else None),
            event=event,
            ip_address=ip,
            user_agent=ua,
            status=status,
            description=description
        )
    except Exception as e:
        print(f"Error logging admin security event: {e}")

def validate_password_strength(password):
    if not password or not str(password).strip():
        return False, "Password cannot be empty."
    return True, ""

def generate_otp_for_user(user, purpose='LOGIN', new_email=None, new_username=None, request=None):
    AdminOTP.objects.filter(user=user, purpose=purpose, is_used=False).update(is_used=True)

    raw_otp = f"{random.randint(100000, 999999)}"
    otp_hash = hashlib.sha256(raw_otp.encode('utf-8')).hexdigest()
    expires_at = timezone.now() + datetime.timedelta(minutes=5)

    AdminOTP.objects.create(
        user=user,
        otp_hash=otp_hash,
        purpose=purpose,
        new_email=new_email,
        new_username=new_username,
        expires_at=expires_at,
        attempt_count=0,
        is_used=False
    )

    if request:
        log_admin_security_event(user, 'OTP_SENT', request, 'SUCCESS', f"OTP generated for {purpose}")

    target_email = new_email or user.email
    if target_email:
        try:
            from .email_service import send_dynamic_email
            subject = f"EduTrust LMS Super Admin - {purpose.replace('_', ' ').title()} OTP Code"
            body = (
                f"Hello {user.get_full_name() or user.username},\n\n"
                f"Your EduTrust LMS Super Admin 6-digit verification code is: {raw_otp}\n\n"
                f"This code will expire in 5 minutes. Do NOT share this OTP with anyone.\n\n"
                f"Regards,\nEduTrust LMS Security Team"
            )
            send_dynamic_email(target_email, subject, body, fail_silently=True)
        except Exception as e:
            print(f"Error sending OTP email: {e}")

    return raw_otp

def verify_otp_for_user(user, purpose, otp_code, request=None):
    raw_otp = str(otp_code).strip()
    if len(raw_otp) != 6:
        return False, "OTP must be a 6-digit number.", None

    otp_obj = AdminOTP.objects.filter(user=user, purpose=purpose, is_used=False).order_by('-created_at').first()
    if not otp_obj:
        return False, "No active OTP found. Please request a new OTP.", None

    if timezone.now() > otp_obj.expires_at:
        otp_obj.is_used = True
        otp_obj.save()
        if request:
            log_admin_security_event(user, 'OTP_FAILED', request, 'FAILED', "OTP expired")
        return False, "This OTP has expired. Please request a new OTP.", None

    if otp_obj.attempt_count >= 5:
        otp_obj.is_used = True
        otp_obj.save()
        if request:
            log_admin_security_event(user, 'OTP_FAILED', request, 'FAILED', "Too many failed OTP attempts")
        return False, "Too many failed attempts. This OTP is now invalid. Please request a new one.", None

    input_hash = hashlib.sha256(raw_otp.encode('utf-8')).hexdigest()
    if input_hash != otp_obj.otp_hash:
        otp_obj.attempt_count += 1
        otp_obj.save()
        if request:
            log_admin_security_event(user, 'OTP_FAILED', request, 'FAILED', f"Incorrect OTP attempt ({otp_obj.attempt_count}/5)")
        return False, f"Incorrect OTP code. {5 - otp_obj.attempt_count} attempts remaining.", None

    otp_obj.is_used = True
    otp_obj.save()
    if request:
        log_admin_security_event(user, 'OTP_VERIFIED', request, 'SUCCESS', f"OTP verified for {purpose}")
    return True, "OTP verified successfully.", otp_obj


# ===========================
def admin_root_view(request):
    return redirect('/admin/login/')

def admin_login_view(request):
    next_param = request.GET.get('next', '').strip()
    if next_param in ('/admin/', '/admin', '/admin/login/', '/admin/login'):
        return redirect('/admin/login/')

    # Enforce fresh login entry every time: clear pending admin login state without destroying overall session
    request.session.pop('admin_pending_user_id', None)
    request.session.pop('admin_otp_purpose', None)

    next_url = request.GET.get('next', '/admin/dashboard/')
    expired = request.GET.get('expired', '0')
    return render(request, 'admin/login.html', {'next_url': next_url, 'expired': expired, 'initial_state': 'login'})

def admin_verify_otp_view(request):
    pending_user_id = request.session.get('admin_pending_user_id') or request.session.get('recovery_user_id')
    purpose = request.GET.get('purpose', request.session.get('admin_otp_purpose', 'LOGIN'))
    
    user = User.objects.filter(id=pending_user_id).first() if pending_user_id else None
    if not user:
        user = User.objects.filter(is_superuser=True, is_active=True).first() or User.objects.filter(is_staff=True, is_active=True).first()
        if user:
            request.session['admin_pending_user_id'] = user.id
            request.session['admin_otp_purpose'] = purpose

    masked_email = user.email if user else ''
    if masked_email and '@' in masked_email:
        parts = masked_email.split('@')
        name_part = parts[0]
        masked_email = (name_part[:2] + '***' + name_part[-1:] if len(name_part) > 3 else name_part[0] + '***') + '@' + parts[1]

    next_url = request.session.get('admin_login_next', '/admin/dashboard/')
    return render(request, 'admin/login.html', {
        'initial_state': 'otp',
        'masked_email': masked_email or (user.username if user else 'registered email'),
        'purpose': purpose,
        'next_url': next_url,
        'dev_otp': ''
    })

def admin_forgot_password_view(request):
    return render(request, 'admin/login.html', {'initial_state': 'forgot'})

def admin_reset_password_view(request):
    return render(request, 'admin/login.html', {'initial_state': 'update'})

def admin_security_settings_view(request):
    user = request.user
    if not user.is_authenticated or not (user.is_superuser or user.is_staff):
        return redirect('/admin/login/')
    
    security_logs = AdminSecurityLog.objects.filter(user=user).order_by('-timestamp')[:20]
    return render(request, 'admin/security_settings.html', {
        'admin_user': user,
        'security_logs': security_logs
    })

def admin_logout_view(request):
    user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
    if user:
        log_admin_security_event(user, 'LOGOUT', request, 'SUCCESS', f"Super Admin {user.username} logged out")
    logout(request)
    request.session.flush()
    return redirect('/admin/login/')


# ===========================
# AJAX API Authentication Controllers
# ===========================

@csrf_exempt
@require_http_methods(["POST"])
def api_admin_auth_login(request):
    data = json.loads(request.body.decode('utf-8')) if request.content_type == 'application/json' else request.POST
    identifier = (data.get('username_or_email') or data.get('username') or '').strip()
    password = (data.get('password') or '').strip()
    remember_me = data.get('remember_me', False)

    if not identifier or not password:
        return JsonResponse({'status': 'error', 'message': 'Username/Email and Password are required.'}, status=400)

    user = User.objects.filter(Q(username__iexact=identifier) | Q(email__iexact=identifier)).first()
    if not user:
        log_admin_security_event(None, 'LOGIN_FAILED', request, 'FAILED', f"Login attempt for non-existent account: {identifier}")
        return JsonResponse({'status': 'error', 'message': 'Username or Email address is incorrect. Account not found.'}, status=400)

    if not user.is_active:
        log_admin_security_event(user, 'ACCOUNT_LOCKED', request, 'FAILED', "Attempted login to suspended/inactive account")
        return JsonResponse({'status': 'error', 'message': 'Your account is currently unavailable. Please contact system administrator.'}, status=403)

    if not (user.is_superuser or user.is_staff):
        log_admin_security_event(user, 'LOGIN_FAILED', request, 'FAILED', "Non-admin account attempted Super Admin panel access")
        return JsonResponse({'status': 'error', 'message': 'Access Denied. Super Admin privileges required.'}, status=403)

    if not user.check_password(password):
        log_admin_security_event(user, 'LOGIN_FAILED', request, 'FAILED', "Incorrect password")
        return JsonResponse({'status': 'error', 'message': 'Incorrect Password. Please check your password and try again.'}, status=400)

    # Valid Credentials -> Direct Login (No OTP required as requested)
    login(request, user)
    request.session['super_admin_verified'] = True
    request.session['admin_last_activity'] = int(timezone.now().timestamp())

    if remember_me:
        request.session.set_expiry(315360000)  # Persistent session
    else:
        request.session.set_expiry(0)  # Session cookie

    log_admin_security_event(user, 'LOGIN_SUCCESS', request, 'SUCCESS', f"Super Admin {user.username} logged in successfully")

    next_url = data.get('next') or '/admin/dashboard/'
    request.session.pop('admin_pending_user_id', None)
    request.session.pop('admin_otp_purpose', None)

    return JsonResponse({
        'status': 'success',
        'message': 'Login successful! Redirecting to admin dashboard...',
        'redirect_url': next_url
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_admin_auth_verify_otp(request):
    data = json.loads(request.body.decode('utf-8')) if request.content_type == 'application/json' else request.POST
    otp_code = (data.get('otp_code') or '').strip()
    purpose = data.get('purpose', request.session.get('admin_otp_purpose', 'LOGIN'))

    pending_user_id = request.session.get('admin_pending_user_id')
    if not pending_user_id:
        return JsonResponse({'status': 'error', 'message': 'Session expired. Please log in again.'}, status=401)

    user = User.objects.filter(id=pending_user_id).first()
    if not user:
        return JsonResponse({'status': 'error', 'message': 'User account not found.'}, status=404)

    is_valid, msg, otp_obj = verify_otp_for_user(user, purpose, otp_code, request=request)
    if not is_valid:
        return JsonResponse({'status': 'error', 'message': msg}, status=400)

    if purpose == 'LOGIN':
        login(request, user)
        request.session['super_admin_verified'] = True
        request.session['admin_last_activity'] = int(timezone.now().timestamp())
        
        remember_me = request.session.get('admin_remember_me', False)
        if remember_me:
            request.session.set_expiry(315360000) # Permanent persistent session (10 years) until logout or security changes
        else:
            request.session.set_expiry(0) # Session cookie

        log_admin_security_event(user, 'LOGIN_SUCCESS', request, 'SUCCESS', f"Super Admin {user.username} logged in successfully via OTP")

        next_url = request.session.get('admin_login_next') or '/admin/dashboard/'
        request.session.pop('admin_pending_user_id', None)
        request.session.pop('admin_otp_purpose', None)

        return JsonResponse({
            'status': 'success',
            'message': 'OTP verified! Welcome to Super Admin Portal.',
            'redirect_url': next_url
        })
    
    elif purpose == 'PASSWORD_RESET':
        request.session['admin_reset_user_id'] = user.id
        request.session.pop('admin_pending_user_id', None)
        return JsonResponse({
            'status': 'success',
            'message': 'OTP verified successfully! Set your new password.',
            'redirect_url': '/admin/reset-password/'
        })

    elif purpose == 'USERNAME_CHANGE' and otp_obj and otp_obj.new_username:
        old_uname = user.username
        user.username = otp_obj.new_username
        user.save()
        log_admin_security_event(user, 'USERNAME_CHANGED', request, 'SUCCESS', f"Username changed from {old_uname} to {user.username}")
        request.session.pop('admin_pending_user_id', None)
        return JsonResponse({'status': 'success', 'message': f'Username updated successfully to {user.username}!'})

    elif purpose == 'EMAIL_CHANGE' and otp_obj and otp_obj.new_email:
        old_email = user.email
        user.email = otp_obj.new_email
        user.save()
        log_admin_security_event(user, 'EMAIL_CHANGED', request, 'SUCCESS', f"Email changed from {old_email} to {user.email}")
        request.session.pop('admin_pending_user_id', None)
        return JsonResponse({'status': 'success', 'message': f'Email updated successfully to {user.email}!'})

    return JsonResponse({'status': 'success', 'message': 'OTP verified successfully.'})


@csrf_exempt
@require_http_methods(["POST"])
def api_admin_auth_resend_otp(request):
    pending_user_id = request.session.get('admin_pending_user_id')
    if not pending_user_id:
        return JsonResponse({'status': 'error', 'message': 'Session expired. Please start login process again.'}, status=401)

    user = User.objects.filter(id=pending_user_id).first()
    if not user:
        return JsonResponse({'status': 'error', 'message': 'User account not found.'}, status=404)

    last_time = request.session.get('admin_otp_time', 0)
    now_ts = int(timezone.now().timestamp())
    if now_ts - last_time < 60:
        remaining = 60 - (now_ts - last_time)
        return JsonResponse({'status': 'error', 'message': f'Please wait {remaining} seconds before requesting a new OTP.'}, status=429)

    purpose = request.session.get('admin_otp_purpose', 'LOGIN')
    raw_otp = generate_otp_for_user(user, purpose, request=request)
    request.session['admin_otp_time'] = now_ts

    return JsonResponse({
        'status': 'success',
        'message': 'A new 6-digit OTP code has been sent to your email.'
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_admin_auth_forgot_password(request):
    data = json.loads(request.body.decode('utf-8')) if request.content_type == 'application/json' else request.POST
    identifier = (data.get('username_or_email') or '').strip()

    if not identifier:
        return JsonResponse({'status': 'error', 'message': 'Username or Email is required.'}, status=400)

    user = User.objects.filter(Q(username__iexact=identifier) | Q(email__iexact=identifier)).first()
    if user and (user.is_superuser or user.is_staff):
        request.session['admin_pending_user_id'] = user.id
        request.session['admin_otp_purpose'] = 'PASSWORD_RESET'
        request.session['admin_otp_time'] = int(timezone.now().timestamp())
        raw_otp = generate_otp_for_user(user, 'PASSWORD_RESET', request=request)
        print(f"[DEVELOPMENT NOTICE] Forgot Password Reset OTP for {user.username}: {raw_otp}")

    return JsonResponse({
        'status': 'success',
        'message': 'If an account matches your entry, an OTP code has been sent to your email.',
        'redirect_url': '/admin/verify-otp/?purpose=PASSWORD_RESET'
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_admin_auth_reset_password(request):
    reset_user_id = request.session.get('admin_reset_user_id')
    if not reset_user_id:
        return JsonResponse({'status': 'error', 'message': 'Session expired. Please request password reset again.'}, status=401)

    user = User.objects.filter(id=reset_user_id).first()
    if not user:
        return JsonResponse({'status': 'error', 'message': 'User account not found.'}, status=404)

    data = json.loads(request.body.decode('utf-8')) if request.content_type == 'application/json' else request.POST
    new_pass = (data.get('new_password') or '').strip()
    conf_pass = (data.get('confirm_password') or '').strip()

    if not new_pass or not conf_pass:
        return JsonResponse({'status': 'error', 'message': 'New Password and Confirm Password are required.'}, status=400)

    if new_pass != conf_pass:
        return JsonResponse({'status': 'error', 'message': 'New password and confirm password do not match.'}, status=400)

    is_valid, msg = validate_password_strength(new_pass)
    if not is_valid:
        return JsonResponse({'status': 'error', 'message': msg}, status=400)

    user.set_password(new_pass)
    user.save()
    log_admin_security_event(user, 'PASSWORD_RESET', request, 'SUCCESS', "Super Admin password reset via OTP")

    request.session.flush()
    return JsonResponse({
        'status': 'success',
        'message': 'Your password has been reset successfully! Please log in with your new password.',
        'redirect_url': '/admin/login/'
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_admin_auth_change_password(request):
    user = request.user
    if not user.is_authenticated or not (user.is_superuser or user.is_staff):
        return JsonResponse({'status': 'error', 'message': 'Super Admin authorization required.'}, status=401)

    data = json.loads(request.body.decode('utf-8')) if request.content_type == 'application/json' else request.POST
    cur_pass = (data.get('current_password') or '').strip()
    new_pass = (data.get('new_password') or '').strip()
    conf_pass = (data.get('confirm_password') or '').strip()

    if not cur_pass or not new_pass or not conf_pass:
        return JsonResponse({'status': 'error', 'message': 'All password fields are required.'}, status=400)

    if not user.check_password(cur_pass):
        return JsonResponse({'status': 'error', 'message': 'Current password is incorrect.'}, status=400)

    if cur_pass == new_pass:
        return JsonResponse({'status': 'error', 'message': 'New password cannot be the same as your current password.'}, status=400)

    if new_pass != conf_pass:
        return JsonResponse({'status': 'error', 'message': 'New password and confirm password do not match.'}, status=400)

    is_valid, msg = validate_password_strength(new_pass)
    if not is_valid:
        return JsonResponse({'status': 'error', 'message': msg}, status=400)

    user.set_password(new_pass)
    user.save()
    update_session_auth_hash(request, user)
    log_admin_security_event(user, 'PASSWORD_CHANGED', request, 'SUCCESS', "Super Admin password changed from security settings")

    return JsonResponse({'status': 'success', 'message': 'Your password has been changed successfully!'})


@csrf_exempt
@require_http_methods(["POST"])
def api_admin_auth_change_username(request):
    user = request.user
    if not user.is_authenticated or not (user.is_superuser or user.is_staff):
        return JsonResponse({'status': 'error', 'message': 'Super Admin authorization required.'}, status=401)

    data = json.loads(request.body.decode('utf-8')) if request.content_type == 'application/json' else request.POST
    cur_pass = (data.get('current_password') or '').strip()
    new_username = (data.get('new_username') or '').strip()

    if not cur_pass or not new_username:
        return JsonResponse({'status': 'error', 'message': 'Current Password and New Username are required.'}, status=400)

    if not user.check_password(cur_pass):
        return JsonResponse({'status': 'error', 'message': 'Current password is incorrect.'}, status=400)

    if User.objects.filter(username__iexact=new_username).exclude(id=user.id).exists():
        return JsonResponse({'status': 'error', 'message': 'This username is already taken. Please choose another.'}, status=400)

    request.session['admin_pending_user_id'] = user.id
    request.session['admin_otp_purpose'] = 'USERNAME_CHANGE'
    raw_otp = generate_otp_for_user(user, 'USERNAME_CHANGE', new_username=new_username, request=request)
    print(f"[DEVELOPMENT NOTICE] Username Change OTP for {user.username}: {raw_otp}")

    return JsonResponse({
        'status': 'success',
        'message': f'OTP verification required. Code sent to {user.email}.',
        'redirect_url': '/admin/verify-otp/?purpose=USERNAME_CHANGE'
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_admin_auth_change_email(request):
    user = request.user
    if not user.is_authenticated or not (user.is_superuser or user.is_staff):
        return JsonResponse({'status': 'error', 'message': 'Super Admin authorization required.'}, status=401)

    data = json.loads(request.body.decode('utf-8')) if request.content_type == 'application/json' else request.POST
    cur_pass = (data.get('current_password') or '').strip()
    new_email = (data.get('new_email') or '').strip()

    if not cur_pass or not new_email:
        return JsonResponse({'status': 'error', 'message': 'Current Password and New Email are required.'}, status=400)

    if not user.check_password(cur_pass):
        return JsonResponse({'status': 'error', 'message': 'Current password is incorrect.'}, status=400)

    if User.objects.filter(email__iexact=new_email).exclude(id=user.id).exists():
        return JsonResponse({'status': 'error', 'message': 'This email address is already associated with another account.'}, status=400)

    request.session['admin_pending_user_id'] = user.id
    request.session['admin_otp_purpose'] = 'EMAIL_CHANGE'
    raw_otp = generate_otp_for_user(user, 'EMAIL_CHANGE', new_email=new_email, request=request)
    print(f"[DEVELOPMENT NOTICE] Email Change OTP for {user.username} sent to {new_email}: {raw_otp}")

    return JsonResponse({
        'status': 'success',
        'message': f'OTP verification required. Code sent to {new_email}.',
        'redirect_url': '/admin/verify-otp/?purpose=EMAIL_CHANGE'
    })

# ===========================
# OTP-First Account Recovery API Controllers
# ===========================

@csrf_exempt
@require_http_methods(["POST"])
def api_admin_auth_recovery_send_otp(request):
    """
    Step 1 of Account Recovery: Enter Username or Email -> Generate & Send OTP to Registered Email.
    Initializes temporary recovery session with recovery_otp_verified = False.
    """
    data = json.loads(request.body.decode('utf-8')) if request.content_type == 'application/json' else request.POST
    identifier = (data.get('username_or_email') or '').strip()

    if not identifier:
        return JsonResponse({'status': 'error', 'message': 'Username or Email address is required.'}, status=400)

    user = User.objects.filter(Q(username__iexact=identifier) | Q(email__iexact=identifier)).first()
    if not user or not user.is_active or not (user.is_superuser or user.is_staff):
        return JsonResponse({'status': 'error', 'message': 'Account not found or access denied. Admin privileges required.'}, status=400)

    # Initialize Recovery Session
    now_ts = int(timezone.now().timestamp())
    request.session['recovery_user_id'] = user.id
    request.session['recovery_started'] = True
    request.session['recovery_otp_verified'] = False
    request.session['recovery_expires_at'] = now_ts + 1800 # 10 minutes
    request.session['admin_otp_purpose'] = 'PASSWORD_RESET'
    request.session['admin_otp_time'] = now_ts

    raw_otp = generate_otp_for_user(user, 'PASSWORD_RESET', request=request)
    log_admin_security_event(user, 'PASSWORD_RESET_REQUESTED', request, 'SUCCESS', f"Password reset requested for {user.username}")
    print(f"[DEVELOPMENT NOTICE] Account Recovery OTP for {user.username}: {raw_otp}")

    masked_email = user.email
    if masked_email and '@' in masked_email:
        parts = masked_email.split('@')
        name_part = parts[0]
        masked_email = (name_part[:2] + '***' + name_part[-1:] if len(name_part) > 3 else name_part[0] + '***') + '@' + parts[1]

    return JsonResponse({
        'status': 'success',
        'message': f"Verification OTP sent to {masked_email}.",
        'masked_email': masked_email or 'registered email',
        'has_account': True
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_admin_auth_recovery_verify_otp(request):
    """
    Step 2 of Account Recovery: Verify 6-digit OTP code.
    Sets recovery_otp_verified = True upon success.
    """
    data = json.loads(request.body.decode('utf-8')) if request.content_type == 'application/json' else request.POST
    otp_code = (data.get('otp_code') or '').strip()

    recovery_user_id = request.session.get('recovery_user_id')
    now_ts = int(timezone.now().timestamp())
    expires_at = request.session.get('recovery_expires_at', 0)

    if not recovery_user_id or now_ts > expires_at:
        return JsonResponse({'status': 'error', 'message': 'Your recovery session has expired. Please start the recovery process again.'}, status=401)

    user = User.objects.filter(id=recovery_user_id).first()
    if not user:
        return JsonResponse({'status': 'error', 'message': 'User account not found.'}, status=404)

    is_valid, msg, otp_obj = verify_otp_for_user(user, 'PASSWORD_RESET', otp_code, request=request)
    if not is_valid:
        return JsonResponse({'status': 'error', 'message': msg}, status=400)

    # UNLOCK RECOVERY SESSION STATE
    request.session['recovery_otp_verified'] = True
    log_admin_security_event(user, 'OTP_VERIFIED', request, 'SUCCESS', f"Recovery OTP verified for {user.username}")

    return JsonResponse({
        'status': 'success',
        'message': 'OTP Verified Successfully! Choose your recovery option.',
        'otp_verified': True
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_admin_auth_recovery_change_password(request):
    """
    Step 3 Option A: Change Password.
    CRITICAL SERVER-SIDE SECURITY CHECK: Requires recovery_otp_verified == True.
    """
    recovery_user_id = request.session.get('recovery_user_id')
    otp_verified = request.session.get('recovery_otp_verified', False)
    now_ts = int(timezone.now().timestamp())
    expires_at = request.session.get('recovery_expires_at', 0)

    # STRICT BACKEND ENFORCEMENT
    if not recovery_user_id or not otp_verified or now_ts > expires_at:
        log_admin_security_event(None, 'LOGIN_FAILED', request, 'FAILED', "Attempted to bypass OTP verification for password change")
        return JsonResponse({'status': 'error', 'message': 'Access Denied. Successful OTP verification is strictly required before changing password.'}, status=403)

    user = User.objects.filter(id=recovery_user_id).first()
    if not user:
        return JsonResponse({'status': 'error', 'message': 'User account not found.'}, status=404)

    data = json.loads(request.body.decode('utf-8')) if request.content_type == 'application/json' else request.POST
    new_pass = (data.get('new_password') or '').strip()
    conf_pass = (data.get('confirm_password') or '').strip()

    if not new_pass or not conf_pass:
        return JsonResponse({'status': 'error', 'message': 'New Password and Confirm Password are required.'}, status=400)

    if new_pass != conf_pass:
        return JsonResponse({'status': 'error', 'message': 'New password and confirm password do not match.'}, status=400)

    is_valid, msg = validate_password_strength(new_pass)
    if not is_valid:
        return JsonResponse({'status': 'error', 'message': msg}, status=400)

    user.set_password(new_pass)
    user.save()
    log_admin_security_event(user, 'PASSWORD_CHANGED', request, 'SUCCESS', f"Super Admin {user.username} password changed via account recovery")

    # Invalidate recovery & all existing sessions
    request.session.flush()

    # Send Security Email Notification
    if user.email:
        try:
            from .email_service import send_dynamic_email
            subject = "EduTrust LMS Super Admin - Security Alert: Password Changed"
            message = f"Hello {user.get_full_name() or user.username},\n\nYour EduTrust LMS Super Admin password was changed successfully via account recovery.\n\nIf you did not make this change, please contact system administrator immediately.\n\nRegards,\nEduTrust LMS Security Team"
            send_dynamic_email(user.email, subject, message, fail_silently=True)
        except Exception as e:
            print(f"Error sending security email: {e}")

    return JsonResponse({
        'status': 'success',
        'message': 'Password changed successfully. Please login again.',
        'redirect_url': '/admin/login/'
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_admin_auth_recovery_change_identity(request):
    """
    Step 3 Option B: Change Username or Email.
    CRITICAL SERVER-SIDE SECURITY CHECK: Requires recovery_otp_verified == True.
    """
    recovery_user_id = request.session.get('recovery_user_id')
    otp_verified = request.session.get('recovery_otp_verified', False)
    now_ts = int(timezone.now().timestamp())
    expires_at = request.session.get('recovery_expires_at', 0)

    if not recovery_user_id or not otp_verified or now_ts > expires_at:
        return JsonResponse({'status': 'error', 'message': 'Access Denied. Successful OTP verification is strictly required before changing account details.'}, status=403)

    user = User.objects.filter(id=recovery_user_id).first()
    if not user:
        return JsonResponse({'status': 'error', 'message': 'User account not found.'}, status=404)

    data = json.loads(request.body.decode('utf-8')) if request.content_type == 'application/json' else request.POST
    new_username = (data.get('new_username') or '').strip()
    new_email = (data.get('new_email') or '').strip()

    changes = []
    if new_username and new_username != user.username:
        if User.objects.filter(username__iexact=new_username).exclude(id=user.id).exists():
            return JsonResponse({'status': 'error', 'message': 'This username is already taken by another account.'}, status=400)
        old_uname = user.username
        user.username = new_username
        user.save()
        changes.append(f"Username changed from {old_uname} to {user.username}")
        log_admin_security_event(user, 'USERNAME_CHANGED', request, 'SUCCESS', f"Username changed to {user.username}")

    if new_email and new_email != user.email:
        if User.objects.filter(email__iexact=new_email).exclude(id=user.id).exists():
            return JsonResponse({'status': 'error', 'message': 'This email address is already associated with another account.'}, status=400)
        old_email = user.email
        user.email = new_email
        user.save()
        changes.append(f"Email changed from {old_email} to {user.email}")
        log_admin_security_event(user, 'EMAIL_CHANGED', request, 'SUCCESS', f"Email changed to {user.email}")

    if not changes:
        return JsonResponse({'status': 'error', 'message': 'No changes detected.'}, status=400)

    request.session.flush()
    return JsonResponse({
        'status': 'success',
        'message': 'Account details updated successfully. Please login again with your new credentials.',
        'redirect_url': '/admin/login/'
    })

@csrf_exempt
@require_http_methods(["POST"])
def api_admin_auth_recovery_update_account(request):
    """
    Unified Account Recovery Controller:
    Allows changing Username, Email, AND/OR Password together in ONE single form submission
    after OTP verification. STRICTLY checks recovery_otp_verified == True.
    """
    recovery_user_id = request.session.get('recovery_user_id')
    otp_verified = request.session.get('recovery_otp_verified', False)
    now_ts = int(timezone.now().timestamp())
    expires_at = request.session.get('recovery_expires_at', 0)

    if not recovery_user_id or not otp_verified or now_ts > expires_at:
        log_admin_security_event(None, 'LOGIN_FAILED', request, 'FAILED', "Attempted bypass of OTP verification for account update")
        return JsonResponse({'status': 'error', 'message': 'Access Denied. Successful OTP verification is strictly required before updating account details.'}, status=403)

    user = User.objects.filter(id=recovery_user_id).first()
    if not user:
        return JsonResponse({'status': 'error', 'message': 'User account not found.'}, status=404)

    data = json.loads(request.body.decode('utf-8')) if request.content_type == 'application/json' else request.POST
    new_username = (data.get('new_username') or '').strip()
    new_email = (data.get('new_email') or '').strip()
    new_pass = (data.get('new_password') or '').strip()
    conf_pass = (data.get('confirm_password') or '').strip()

    if not new_username and not new_email and not new_pass:
        return JsonResponse({'status': 'error', 'message': 'Please fill in at least one field (Username, Email, or Password) to update.'}, status=400)

    changes_log = []

    # 1. Process Username Update
    if new_username and new_username != user.username:
        if User.objects.filter(username__iexact=new_username).exclude(id=user.id).exists():
            return JsonResponse({'status': 'error', 'message': f"The username '{new_username}' is already taken. Please choose another."}, status=400)
        old_uname = user.username
        user.username = new_username
        changes_log.append(f"Username changed from {old_uname} to {new_username}")
        log_admin_security_event(user, 'USERNAME_CHANGED', request, 'SUCCESS', f"Username updated to {new_username} via account recovery")

    # 2. Process Email Update
    if new_email and new_email != user.email:
        if User.objects.filter(email__iexact=new_email).exclude(id=user.id).exists():
            return JsonResponse({'status': 'error', 'message': f"The email '{new_email}' is already used by another account."}, status=400)
        old_email = user.email
        user.email = new_email
        changes_log.append(f"Email changed from {old_email} to {new_email}")
        log_admin_security_event(user, 'EMAIL_CHANGED', request, 'SUCCESS', f"Email updated to {new_email} via account recovery")

    # 3. Process Password Update
    if new_pass:
        if not conf_pass:
            return JsonResponse({'status': 'error', 'message': 'Please confirm your new password.'}, status=400)
        if new_pass != conf_pass:
            return JsonResponse({'status': 'error', 'message': 'New password and confirm password do not match.'}, status=400)

        is_valid, msg = validate_password_strength(new_pass)
        if not is_valid:
            return JsonResponse({'status': 'error', 'message': msg}, status=400)

        user.set_password(new_pass)
        changes_log.append("Password updated")
        log_admin_security_event(user, 'PASSWORD_CHANGED', request, 'SUCCESS', "Password updated via account recovery")

    user.save()

    # Invalidate recovery session & active login sessions
    request.session.flush()

    # Send Notification Email
    if user.email:
        try:
            from .email_service import send_dynamic_email
            subject = "EduTrust LMS Super Admin - Account Recovery Updated"
            message = (
                f"Hello {user.get_full_name() or user.username},\n\n"
                f"Your EduTrust LMS Super Admin account credentials were updated successfully:\n"
                f"- " + "\n- ".join(changes_log) + "\n\n"
                f"If you did not make these changes, please contact system administrator immediately.\n\n"
                f"Regards,\nEduTrust LMS Security Team"
            )
            send_dynamic_email(user.email, subject, message, fail_silently=True)
        except Exception as e:
            print(f"Error sending security notification: {e}")

    return JsonResponse({
        'status': 'success',
        'message': 'Super Admin account credentials updated successfully! Please log in with your new credentials.',
        'redirect_url': '/admin/login/'
    })
