"""
EduTrust LMS - Centralized Dynamic Email & Notification Service
Dynamically loads and applies SMTP credentials from SystemSetting database table.
Supports transactional OTPs, password reset emails, notifications, and connection testing.
"""

import random
import logging
from django.conf import settings
from django.utils import timezone
from django.core.mail.backends.smtp import EmailBackend
from django.core.mail import EmailMultiAlternatives

logger = logging.getLogger(__name__)


def get_smtp_config():
    """
    Fetches the current active SMTP configuration from SystemSetting table.
    """
    try:
        from .models import SystemSetting
        settings_map = {}
        for s in SystemSetting.objects.filter(category='communication', is_active=True):
            settings_map[s.key] = s.value

        email_enabled = str(settings_map.get('email_enabled', 'true')).lower() in ['true', '1', 'yes', 'on']
        host = (settings_map.get('smtp_host') or 'smtp.gmail.com').strip()
        
        try:
            port = int(settings_map.get('smtp_port', 587))
        except (ValueError, TypeError):
            port = 587

        username = (settings_map.get('smtp_username') or '').strip()
        password = (settings_map.get('smtp_password') or '').strip()
        
        use_tls = str(settings_map.get('smtp_use_tls', 'true')).lower() in ['true', '1', 'yes', 'on']
        use_ssl = str(settings_map.get('smtp_use_ssl', 'false')).lower() in ['true', '1', 'yes', 'on']
        
        if port == 465:
            use_ssl = True
            use_tls = False
        elif port == 587:
            use_tls = True
            use_ssl = False

        from_email = (settings_map.get('from_email') or '').strip()
        if not from_email or from_email == 'noreply@edutrust.com':
            from_email = username or 'noreply@edutrust.com'

        reply_to = (settings_map.get('reply_to_email') or 'support@edutrust.com').strip()

        return {
            'enabled': email_enabled,
            'host': host,
            'port': port,
            'username': username,
            'password': password,
            'use_tls': use_tls,
            'use_ssl': use_ssl,
            'from_email': from_email,
            'reply_to': reply_to,
        }
    except Exception as e:
        logger.warning(f"Failed to query SystemSetting for SMTP config: {e}")
        return {
            'enabled': True,
            'host': 'smtp.gmail.com',
            'port': 587,
            'username': '',
            'password': '',
            'use_tls': True,
            'use_ssl': False,
            'from_email': 'noreply@edutrust.com',
            'reply_to': 'support@edutrust.com',
        }


def get_dynamic_email_backend(custom_config=None):
    """
    Creates a dynamic Django SMTP EmailBackend instance using configured credentials.
    """
    cfg = custom_config or get_smtp_config()
    
    if not cfg.get('enabled', True):
        return None, "System email delivery is disabled in Email Settings."

    host = cfg.get('host', 'smtp.gmail.com')
    port = cfg.get('port', 587)
    username = cfg.get('username', '')
    password = cfg.get('password', '')
    use_tls = cfg.get('use_tls', True)
    use_ssl = cfg.get('use_ssl', False)

    try:
        backend = EmailBackend(
            host=host,
            port=port,
            username=username,
            password=password,
            use_tls=use_tls,
            use_ssl=use_ssl,
            timeout=10,
            fail_silently=False
        )
        return backend, None
    except Exception as e:
        return None, str(e)


def send_dynamic_email(to_emails, subject, body_text, html_content=None, from_email=None, reply_to=None, fail_silently=False, inline_images=None):
    """
    Sends email dynamically using configured SMTP credentials in SystemSetting.
    Accepts single recipient string or list of recipient strings.
    Sends pure multipart/alternative text/html email with zero attachment chips.
    """
    if isinstance(to_emails, str):
        to_emails = [to_emails.strip()]
    to_emails = [e for e in to_emails if e and '@' in e]
    
    if not to_emails:
        return False, "No valid recipient email address provided."

    cfg = get_smtp_config()
    if not cfg.get('enabled', True):
        logger.info("Email not sent: Email system is toggled off in settings.")
        return False, "Email system is disabled in Admin Settings."

    backend, err = get_dynamic_email_backend(cfg)
    if not backend:
        return False, err or "Could not initialize SMTP backend."

    # In Gmail SMTP, if from_email doesn't match the authenticated user, Gmail may rewrite or reject it
    effective_from = from_email or cfg.get('from_email') or cfg.get('username') or 'noreply@edutrust.com'
    if 'gmail.com' in cfg.get('host', '') and cfg.get('username'):
        effective_from = f"EduTrust LMS <{cfg.get('username')}>"
    elif not effective_from.endswith('>'):
        effective_from = f"EduTrust LMS <{effective_from}>"

    reply_to_email = reply_to or cfg.get('reply_to')
    reply_to_list = [reply_to_email] if (reply_to_email and '@' in reply_to_email) else None

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=body_text,
            from_email=effective_from,
            to=to_emails,
            reply_to=reply_to_list,
            connection=backend
        )
        if html_content:
            msg.attach_alternative(html_content, "text/html")

        sent_count = msg.send(fail_silently=fail_silently)
        if sent_count > 0:
            logger.info(f"Dynamic email sent successfully to {to_emails} [Subject: {subject}]")
            return True, "Email dispatched successfully."
        return False, "Email backend accepted message but returned 0 sent count."
    except Exception as e:
        logger.error(f"Error dispatching dynamic email to {to_emails}: {e}")
        if not fail_silently:
            return False, str(e)
        return False, str(e)


def send_otp_email(to_email, otp_code, purpose="LOGIN"):
    """
    Sends standard 6-digit OTP verification email to user for Login / Password Reset / 2FA.
    """
    to_email = (to_email or '').strip()
    if not to_email:
        return False, "Invalid recipient email"

    subject = f"EduTrust Security Code: {otp_code}"
    
    if purpose == "LOGIN":
        body_text = f"""Hello,

Your 6-digit OTP for EduTrust Login verification is: {otp_code}

This verification code is valid for 10 minutes. For security reasons, please do not share this code with anyone.

If you did not request this code, please secure your account immediately.

Warm Regards,
EduTrust Learning Platform Team"""

        html_content = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 540px; margin: 0 auto; background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
            <div style="background: linear-gradient(135deg, #2563eb 0%, #4f46e5 100%); padding: 24px; text-align: center; color: white;">
                <h1 style="margin: 0; font-size: 20px; font-weight: 800; letter-spacing: -0.5px;">EduTrust Platform</h1>
                <p style="margin: 4px 0 0 0; font-size: 12px; opacity: 0.9;">Secure Login Authentication</p>
            </div>
            <div style="padding: 32px 24px; text-align: center;">
                <p style="font-size: 14px; color: #475569; margin: 0 0 16px 0;">Use the 6-digit verification code below to complete your login:</p>
                <div style="display: inline-block; background-color: #f1f5f9; border: 2px dashed #cbd5e1; border-radius: 12px; padding: 14px 28px; margin: 8px 0 20px 0;">
                    <span style="font-family: 'Courier New', Courier, monospace; font-size: 32px; font-weight: 800; letter-spacing: 6px; color: #1e293b;">{otp_code}</span>
                </div>
                <p style="font-size: 12px; color: #64748b; margin: 0;">⏱ This code expires in <strong>10 minutes</strong>. Do not share it with anyone.</p>
            </div>
            <div style="background-color: #f8fafc; border-top: 1px solid #f1f5f9; padding: 16px 24px; text-align: center; font-size: 11px; color: #94a3b8;">
                &copy; {timezone.now().year} EduTrust LMS. All rights reserved.
            </div>
        </div>
        """
    else:
        body_text = f"""Hello,

Your 6-digit OTP for EduTrust Password Reset is: {otp_code}

This verification code is valid for 10 minutes. For security reasons, please do not share this code with anyone.

If you did not request a password reset, please ignore this email.

Warm Regards,
EduTrust Learning Platform Team"""

        html_content = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 540px; margin: 0 auto; background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
            <div style="background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%); padding: 24px; text-align: center; color: white;">
                <h1 style="margin: 0; font-size: 20px; font-weight: 800; letter-spacing: -0.5px;">EduTrust Platform</h1>
                <p style="margin: 4px 0 0 0; font-size: 12px; opacity: 0.9;">Password Reset Request</p>
            </div>
            <div style="padding: 32px 24px; text-align: center;">
                <p style="font-size: 14px; color: #475569; margin: 0 0 16px 0;">Use the 6-digit verification code below to reset your password:</p>
                <div style="display: inline-block; background-color: #f1f5f9; border: 2px dashed #cbd5e1; border-radius: 12px; padding: 14px 28px; margin: 8px 0 20px 0;">
                    <span style="font-family: 'Courier New', Courier, monospace; font-size: 32px; font-weight: 800; letter-spacing: 6px; color: #1e293b;">{otp_code}</span>
                </div>
                <p style="font-size: 12px; color: #64748b; margin: 0;">⏱ This code expires in <strong>10 minutes</strong>. Do not share it with anyone.</p>
            </div>
            <div style="background-color: #f8fafc; border-top: 1px solid #f1f5f9; padding: 16px 24px; text-align: center; font-size: 11px; color: #94a3b8;">
                &copy; {timezone.now().year} EduTrust LMS. All rights reserved.
            </div>
        </div>
        """

    return send_dynamic_email(to_email, subject, body_text, html_content=html_content, fail_silently=False)


def send_job_apply_otp_email(to_email, otp_code, job_title="Tuition Requirement"):
    """
    Sends a 6-digit OTP verification email for applying to a Tuition Job.
    """
    to_email = (to_email or '').strip()
    if not to_email:
        return False, "Invalid recipient email"

    subject = f"EduTrust Job Application OTP: {otp_code}"
    
    body_text = f"""Hello,

Your 6-digit verification code to apply for '{job_title}' on EduTrust is: {otp_code}

This code is valid for 10 minutes. Please enter it on the portal to submit your job application.

If you did not request to apply for this tuition requirement, please ignore this email.

Warm Regards,
EduTrust Tuition Platform Team"""

    html_content = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 540px; margin: 0 auto; background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
        <div style="background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); padding: 24px; text-align: center; color: white;">
            <h1 style="margin: 0; font-size: 20px; font-weight: 800; letter-spacing: -0.5px;">EduTrust Tuition Platform</h1>
            <p style="margin: 4px 0 0 0; font-size: 13px; opacity: 0.95;">Tuition Job Application Verification</p>
        </div>
        <div style="padding: 30px 24px; text-align: center;">
            <p style="font-size: 14px; color: #334155; margin: 0 0 8px 0; font-weight: 600;">Applying for: <span style="color: #2563eb;">{job_title}</span></p>
            <p style="font-size: 13px; color: #64748b; margin: 0 0 16px 0;">Use the 6-digit verification code below to confirm and submit your application:</p>
            <div style="display: inline-block; background-color: #f0f7ff; border: 2px dashed #93c5fd; border-radius: 12px; padding: 14px 28px; margin: 8px 0 20px 0;">
                <span style="font-family: 'Courier New', Courier, monospace; font-size: 32px; font-weight: 800; letter-spacing: 6px; color: #1e40af;">{otp_code}</span>
            </div>
            <p style="font-size: 12px; color: #64748b; margin: 0;">⏱ This code expires in <strong>10 minutes</strong>. Do not share it with anyone.</p>
        </div>
        <div style="background-color: #f8fafc; border-top: 1px solid #f1f5f9; padding: 16px 24px; text-align: center; font-size: 11px; color: #94a3b8;">
            &copy; {timezone.now().year} EduTrust LMS. All rights reserved.
        </div>
    </div>
    """

    return send_dynamic_email(to_email, subject, body_text, html_content=html_content, fail_silently=False)


# Alias for backward compatibility
send_job_application_otp_email = send_job_apply_otp_email


def send_job_application_success_email(to_email, application_id, job_title="Tuition Requirement", job_id="", details=None):
    """
    Sends full tuition job application confirmation email to the applicant.
    """
    to_email = (to_email or '').strip()
    if not to_email:
        return False, "Invalid recipient email"

    applicant_name = (details.get('name') if isinstance(details, dict) else '') or 'Tutor'
    applicant_mobile = (details.get('mobile') if isinstance(details, dict) else '') or ''

    subject = f"Application Confirmed ({application_id}) - EduTrust"
    now_str = timezone.now().strftime("%d %b %Y, %I:%M %p")
    
    body_text = f"""Hello {applicant_name},

Congratulations! Your application for the tuition requirement '{job_title}' has been received and confirmed successfully on EduTrust.

Application Details:
- Application ID: {application_id}
- Applicant Name: {applicant_name}
- Requirement: {job_title}
- Job ID: {job_id or 'N/A'}
- Applied On: {now_str}
- Status: Under Review / Sent to Admin

Our academic team will review your application and connect you with the student/parent shortly.

Thank you for choosing EduTrust!

Warm Regards,
EduTrust Tuition Platform Team
support@edutrust.com"""

    html_content = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 580px; margin: 0 auto; background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 20px; overflow: hidden; box-shadow: 0 6px 18px rgba(0,0,0,0.06);">
        <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 26px; text-align: center; color: white;">
            <div style="font-size: 32px; margin-bottom: 6px;">🎉</div>
            <h1 style="margin: 0; font-size: 22px; font-weight: 800; letter-spacing: -0.5px;">Application Submitted Successfully!</h1>
            <p style="margin: 4px 0 0 0; font-size: 13px; opacity: 0.95;">EduTrust Tuition Platform</p>
        </div>
        
        <div style="padding: 28px 24px;">
            <p style="font-size: 14px; color: #334155; margin: 0 0 16px 0; line-height: 1.6;">
                Hello <strong>{applicant_name}</strong>,<br>
                Thank you for applying. Your application for the following tuition requirement has been verified and registered on our platform.
            </p>

            <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 14px; padding: 18px; margin-bottom: 20px;">
                <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
                    <tr>
                        <td style="padding: 6px 0; color: #64748b; font-weight: 600; width: 40%;">Application ID:</td>
                        <td style="padding: 6px 0; color: #0f172a; font-weight: 800; font-family: monospace; font-size: 14px;">{application_id}</td>
                    </tr>
                    <tr>
                        <td style="padding: 6px 0; color: #64748b; font-weight: 600;">Tuition Requirement:</td>
                        <td style="padding: 6px 0; color: #2563eb; font-weight: 700;">{job_title}</td>
                    </tr>
                    <tr>
                        <td style="padding: 6px 0; color: #64748b; font-weight: 600;">Submission Date:</td>
                        <td style="padding: 6px 0; color: #334155; font-weight: 600;">{now_str}</td>
                    </tr>
                    <tr>
                        <td style="padding: 6px 0; color: #64748b; font-weight: 600;">Current Status:</td>
                        <td style="padding: 6px 0; color: #10b981; font-weight: 700;">✅ Under Review / Verified</td>
                    </tr>
                </table>
            </div>

            <div style="background-color: #ecfdf5; border-left: 4px solid #10b981; padding: 12px 16px; border-radius: 8px; margin-bottom: 20px;">
                <p style="margin: 0; font-size: 12.5px; color: #065f46; line-height: 1.5;">
                    <strong>Next Steps:</strong> Our academic team will match and connect you with the parent/student. You can check updates on the portal.
                </p>
            </div>

            <p style="font-size: 12px; color: #64748b; margin: 0; text-align: center;">
                Need assistance? Feel free to contact our support team.
            </p>
        </div>

        <div style="background-color: #f8fafc; border-top: 1px solid #f1f5f9; padding: 16px 24px; text-align: center; font-size: 11px; color: #94a3b8;">
            &copy; {timezone.now().year} EduTrust LMS. All rights reserved.
        </div>
    </div>
    """

    return send_dynamic_email(to_email, subject, body_text, html_content=html_content, fail_silently=False)

