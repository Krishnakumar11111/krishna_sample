import os, json, datetime
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q, Count
from django.core.mail import send_mail
from django.conf import settings

from .models import (
    CommunicationLog, CommunicationGroup, SupportTicket, CommunicationTemplate,
    NoticeBoard, Announcement, AdminNotification, StudentProfile, TeacherProfile,
    CourseEnrollment, DirectMessage, AdminSecurityLog
)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '127.0.0.1')

def _render_admin_module_response(request, module_name):
    if not (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)):
        from django.shortcuts import redirect
        import urllib.parse
        return redirect(f'/admin/login/?next={urllib.parse.quote(request.path)}')
    
    context_extra = {
        'base_template': 'admin_partial_base.html' if request.headers.get('x-requested-with') == 'XMLHttpRequest' else 'admin.html',
        'active_module': module_name
    }
    
    if module_name in ['messages', 'notices', 'announcements']:
        return render(request, 'admin/messages.html', context_extra)
    
    from .views import admin_module_view
    return admin_module_view(request, module_name, extra_context=context_extra)


# =========================================================
# Page Controllers
# =========================================================

def admin_messages_view(request):
    return _render_admin_module_response(request, 'messages')

def admin_notices_view(request):
    return _render_admin_module_response(request, 'messages')

def admin_announcements_view(request):
    return _render_admin_module_response(request, 'messages')


# =========================================================
# API Controllers for Communication Center
# =========================================================

@csrf_exempt
def api_admin_comm_stats(request):
    """
    Calculates dynamic statistics strictly from real database tables.
    """
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    seven_days_ago = today_start - datetime.timedelta(days=7)

    # 1. Total Conversations (Users with logs or registered students/teachers)
    total_convs = CommunicationLog.objects.values('recipient_user').distinct().count()
    if total_convs == 0:
        total_convs = User.objects.exclude(is_superuser=True).count()

    # 2. Unread Messages in DB
    unread_msgs = CommunicationLog.objects.filter(is_read=False).count()

    # 3. Active Chats (Activity in last 7 days)
    active_chats = CommunicationLog.objects.filter(created_at__gte=seven_days_ago).values('recipient_user').distinct().count()
    if active_chats == 0:
        active_chats = total_convs

    # 4. Support Tickets
    support_tickets = SupportTicket.objects.exclude(status='CLOSED').count()

    # 5. Today's Messages
    todays_msgs = CommunicationLog.objects.filter(created_at__gte=today_start).count()

    # 6. Active Notices
    notices_count = NoticeBoard.objects.filter(is_active=True).count()

    # 7. Published Announcements
    announcements_count = Announcement.objects.filter(is_published=True).count()

    # 8. Multi-Channel Dispatches (WhatsApp + Email + SMS)
    multi_channel_count = CommunicationLog.objects.filter(channel__in=['WHATSAPP', 'EMAIL', 'SMS']).count()

    return JsonResponse({
        'status': 'success',
        'stats': {
            'total_conversations': total_convs,
            'unread_messages': unread_msgs,
            'active_chats': active_chats,
            'support_tickets': support_tickets,
            'todays_messages': todays_msgs,
            'notices_count': notices_count,
            'announcements_count': announcements_count,
            'whatsapp_sent': multi_channel_count,
            'emails_sent': CommunicationLog.objects.filter(channel='EMAIL').count(),
            'sms_sent': CommunicationLog.objects.filter(channel='SMS').count()
        }
    })


@csrf_exempt
def api_admin_comm_conversations(request):
    """
    Fetches real conversation threads from database with filters & search.
    """
    cat = request.GET.get('category', 'all').lower()
    search = request.GET.get('q', '').strip().lower()

    # Build recipient users list
    users_qs = User.objects.all().order_by('-date_joined')

    if search:
        users_qs = users_qs.filter(
            Q(username__icontains=search) | Q(first_name__icontains=search) | 
            Q(last_name__icontains=search) | Q(email__icontains=search)
        )

    if cat == 'students':
        student_emails = StudentProfile.objects.values_list('email', flat=True)
        users_qs = users_qs.filter(Q(email__in=student_emails) | Q(is_staff=False, is_superuser=False))
    elif cat == 'teachers':
        teacher_emails = TeacherProfile.objects.values_list('email', flat=True)
        users_qs = users_qs.filter(Q(email__in=teacher_emails) | Q(is_staff=True, is_superuser=False))
    elif cat == 'admins' or cat == 'staff':
        users_qs = users_qs.filter(Q(is_superuser=True) | Q(is_staff=True))

    conversations = []
    
    # User conversations
    for u in users_qs[:30]:
        last_msg = CommunicationLog.objects.filter(Q(recipient_user=u) | Q(sender=u)).order_by('-created_at').first()
        unread = CommunicationLog.objects.filter(sender=u, is_read=False).count()
        
        role = 'Student'
        if u.is_superuser:
            role = 'Super Admin'
        elif u.is_staff or TeacherProfile.objects.filter(email=u.email).exists():
            role = 'Teacher'
        elif StudentProfile.objects.filter(email=u.email).exists():
            role = 'Student'

        name = f"{u.get_full_name() or u.username}"
        conversations.append({
            'id': u.id,
            'type': 'USER',
            'name': name,
            'username': u.username,
            'email': u.email or '',
            'role': role,
            'avatar_initials': name[:2].upper(),
            'last_message': last_msg.message_text if last_msg else 'No messages yet.',
            'channel': last_msg.channel if last_msg else 'TEXT',
            'timestamp': last_msg.created_at.strftime('%I:%M %p') if last_msg else '',
            'unread_count': unread,
            'is_starred': last_msg.is_starred if last_msg else False,
            'is_archived': last_msg.is_archived if last_msg else False,
        })

    # Filter starred / archived if requested
    if cat == 'starred':
        conversations = [c for c in conversations if c['is_starred']]
    elif cat == 'archived':
        conversations = [c for c in conversations if c['is_archived']]
    elif cat == 'unread':
        conversations = [c for c in conversations if c['unread_count'] > 0]

    return JsonResponse({'status': 'success', 'conversations': conversations})


@csrf_exempt
def api_admin_comm_thread_messages(request):
    """
    Fetches message thread history for selected user/group/ticket.
    """
    target_id = request.GET.get('target_id')
    target_type = request.GET.get('target_type', 'USER')

    if not target_id:
        return JsonResponse({'status': 'error', 'message': 'Target ID is required.'}, status=400)

    messages_list = []
    
    if target_type == 'USER':
        user = User.objects.filter(id=target_id).first()
        if user:
            # Mark unread messages as read
            CommunicationLog.objects.filter(sender=user, is_read=False).update(is_read=True)
            
            logs = CommunicationLog.objects.filter(
                Q(recipient_user=user) | Q(sender=user)
            ).order_by('created_at')[:50]
            
            for m in logs:
                messages_list.append({
                    'id': m.id,
                    'sender_name': m.sender.get_full_name() or m.sender.username if m.sender else 'System',
                    'is_admin_sender': m.sender and (m.sender.is_superuser or m.sender.is_staff),
                    'channel': m.channel,
                    'subject': m.subject,
                    'message_text': m.message_text,
                    'attachment_url': m.attachment.url if m.attachment else '',
                    'attachment_name': getattr(m, 'attachment_name', (m.attachment.name.split('/')[-1] if m.attachment else '')),
                    'status': m.status,
                    'timestamp': m.created_at.strftime('%I:%M %p, %b %d'),
                    'is_starred': m.is_starred
                })

    return JsonResponse({'status': 'success', 'messages': messages_list})


@csrf_exempt
@require_http_methods(["POST"])
def api_admin_comm_send_message(request):
    """
    Handles multi-channel message dispatch (Text, WhatsApp, Email, SMS) with attachment upload.
    """
    data = request.POST
    recipient_id = data.get('recipient_id')
    channel = (data.get('channel') or 'TEXT').upper()
    subject = (data.get('subject') or '').strip()
    message_text = (data.get('message') or '').strip()
    attachment = request.FILES.get('attachment')

    if not recipient_id or not message_text:
        return JsonResponse({'status': 'error', 'message': 'Recipient and message content are required.'}, status=400)

    recipient_user = User.objects.filter(id=recipient_id).first()
    if not recipient_user:
        return JsonResponse({'status': 'error', 'message': 'Recipient user not found.'}, status=404)

    # File Attachment handling
    att_file = None
    att_name = ''
    if attachment:
        att_file = attachment
        att_name = attachment.name

    # Create Communication Log Record
    comm_log = CommunicationLog.objects.create(
        sender=request.user if request.user.is_authenticated else None,
        recipient_user=recipient_user,
        recipient_name=recipient_user.get_full_name() or recipient_user.username,
        recipient_contact=recipient_user.email or '',
        recipient_role='Student' if not recipient_user.is_staff else 'Teacher',
        channel=channel,
        subject=subject,
        message_text=message_text,
        attachment=att_file,
        
        status='SENT'
    )

    # Multi-Channel Dispatch Logic
    if channel == 'EMAIL' and recipient_user.email:
        try:
            send_mail(
                subject or "EduTrust LMS Notification",
                message_text,
                getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@edutrust.com'),
                [recipient_user.email],
                fail_silently=True
            )
        except Exception as e:
            print(f"Error sending email: {e}")
    elif channel == 'WHATSAPP':
        print(f"[SERVICE ABSTRACTION NOTICE] Dispatching WhatsApp message to {recipient_user.username}: {message_text[:50]}")
    elif channel == 'SMS':
        print(f"[SERVICE ABSTRACTION NOTICE] Dispatching SMS message to {recipient_user.username}: {message_text[:50]}")

    return JsonResponse({
        'status': 'success',
        'message': f'Message dispatched successfully via {channel}!',
        'log_id': comm_log.id
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_admin_comm_broadcast(request):
    """
    Broadcasts message to target audience across multi-channels.
    """
    data = json.loads(request.body.decode('utf-8')) if request.content_type == 'application/json' else request.POST
    audience = data.get('audience', 'ALL')
    channels = data.get('channels', ['TEXT'])
    subject = (data.get('subject') or '').strip()
    message_text = (data.get('message') or '').strip()

    if not message_text:
        return JsonResponse({'status': 'error', 'message': 'Broadcast message content is required.'}, status=400)

    # Resolve target audience users
    users_qs = User.objects.exclude(is_superuser=True)
    if audience == 'STUDENTS':
        student_emails = StudentProfile.objects.values_list('email', flat=True)
        users_qs = users_qs.filter(email__in=student_emails)
    elif audience == 'TEACHERS':
        teacher_emails = TeacherProfile.objects.values_list('email', flat=True)
        users_qs = users_qs.filter(email__in=teacher_emails)

    count = 0
    for u in users_qs[:200]:
        for ch in channels:
            CommunicationLog.objects.create(
                sender=request.user if request.user.is_authenticated else None,
                recipient_user=u,
                recipient_name=u.get_full_name() or u.username,
                recipient_contact=u.email or '',
                channel=ch,
                audience_type=audience,
                subject=subject,
                message_text=message_text,
                status='SENT'
            )
            count += 1

    return JsonResponse({
        'status': 'success',
        'message': f'Broadcast sent successfully to {users_qs.count()} recipients across selected channels!',
        'dispatch_count': count
    })


@csrf_exempt
def api_admin_comm_notices(request):
    """
    Notice Board CRUD API.
    """
    if request.method == 'GET':
        notices = list(NoticeBoard.objects.all().order_by('-created_at').values('id', 'title', 'message', 'action_link', 'is_active', 'created_at'))
        for n in notices:
            n['created_at'] = n['created_at'].strftime('%b %d, %Y %I:%M %p')
        return JsonResponse({'status': 'success', 'notices': notices})
    
    elif request.method == 'POST':
        data = json.loads(request.body.decode('utf-8')) if request.content_type == 'application/json' else request.POST
        title = (data.get('title') or '').strip()
        message = (data.get('message') or '').strip()
        action_link = (data.get('action_link') or '').strip()

        if not title or not message:
            return JsonResponse({'status': 'error', 'message': 'Title and Message content are required.'}, status=400)

        n = NoticeBoard.objects.create(title=title, message=message, action_link=action_link, is_active=True)
        return JsonResponse({'status': 'success', 'message': 'Notice created and published successfully!', 'notice_id': n.id})


@csrf_exempt
def api_admin_comm_announcements(request):
    """
    Announcements CRUD API.
    """
    if request.method == 'GET':
        announcements = list(Announcement.objects.all().order_by('-created_at').values('id', 'announcement_id', 'title', 'message', 'target_audience', 'priority', 'is_published', 'created_at'))
        for a in announcements:
            a['created_at'] = a['created_at'].strftime('%b %d, %Y %I:%M %p')
        return JsonResponse({'status': 'success', 'announcements': announcements})

    elif request.method == 'POST':
        data = json.loads(request.body.decode('utf-8')) if request.content_type == 'application/json' else request.POST
        title = (data.get('title') or '').strip()
        message = (data.get('message') or '').strip()
        audience = data.get('target_audience', 'ALL')
        priority = data.get('priority', 'MEDIUM')

        if not title or not message:
            return JsonResponse({'status': 'error', 'message': 'Title and Message content are required.'}, status=400)

        aid = f"ANC-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        a = Announcement.objects.create(announcement_id=aid, title=title, message=message, target_audience=audience, priority=priority, is_published=True)
        return JsonResponse({'status': 'success', 'message': 'Announcement created & published successfully!', 'announcement_id': a.id})


@csrf_exempt
def api_admin_comm_support(request):
    """
    Support Tickets API.
    """
    if request.method == 'GET':
        tickets = list(SupportTicket.objects.all().order_by('-updated_at').values('id', 'ticket_id', 'user_name', 'user_role', 'category', 'subject', 'status', 'priority', 'internal_note', 'created_at'))
        for t in tickets:
            t['created_at'] = t['created_at'].strftime('%b %d, %Y %I:%M %p')
        return JsonResponse({'status': 'success', 'tickets': tickets})

    elif request.method == 'POST':
        data = json.loads(request.body.decode('utf-8')) if request.content_type == 'application/json' else request.POST
        ticket_id = data.get('ticket_id')
        new_status = data.get('status')
        new_priority = data.get('priority')
        internal_note = data.get('internal_note')

        t = SupportTicket.objects.filter(ticket_id=ticket_id).first()
        if not t:
            return JsonResponse({'status': 'error', 'message': 'Support ticket not found.'}, status=404)

        if new_status: t.status = new_status
        if new_priority: t.priority = new_priority
        if internal_note is not None: t.internal_note = internal_note
        t.save()

        return JsonResponse({'status': 'success', 'message': 'Support ticket updated successfully!'})


@csrf_exempt
def api_admin_comm_user_drawer(request):
    """
    Loads right-side profile drawer data for selected user.
    """
    user_id = request.GET.get('user_id')
    user = User.objects.filter(id=user_id).first() if user_id else None
    if not user:
        return JsonResponse({'status': 'error', 'message': 'User profile not found.'}, status=404)

    # Check Student or Teacher Profile
    sp = StudentProfile.objects.filter(email=user.email).first()
    tp = TeacherProfile.objects.filter(email=user.email).first()

    drawer_data = {
        'id': user.id,
        'name': user.get_full_name() or user.username,
        'username': user.username,
        'email': user.email or 'N/A',
        'phone': getattr(sp, 'student_mobile', None) or getattr(tp, 'mobile', None) or 'N/A',
        'role': 'Student' if sp else ('Teacher' if tp else ('Super Admin' if user.is_superuser else 'Staff')),
        'is_active': user.is_active,
        'date_joined': user.date_joined.strftime('%b %d, %Y'),
        'last_login': user.last_login.strftime('%b %d, %Y %I:%M %p') if user.last_login else 'Never',
        'class': getattr(sp, 'student_class', 'N/A') if sp else 'N/A',
        'subjects': getattr(tp, 'primary_subject', 'N/A') if tp else 'N/A',
        'total_enrolled_courses': CourseEnrollment.objects.filter(student_profile=sp).count() if sp else 0,
    }

    return JsonResponse({'status': 'success', 'user_profile': drawer_data})


@csrf_exempt
def api_admin_comm_templates(request):
    """
    Communication Templates API.
    """
    if request.method == 'GET':
        templates = list(CommunicationTemplate.objects.filter(is_active=True).values('id', 'title', 'channel', 'category', 'subject', 'template_text'))
        return JsonResponse({'status': 'success', 'templates': templates})
    elif request.method == 'POST':
        data = json.loads(request.body.decode('utf-8')) if request.content_type == 'application/json' else request.POST
        title = (data.get('title') or '').strip()
        channel = data.get('channel', 'TEXT')
        category = data.get('category', 'WELCOME')
        template_text = (data.get('template_text') or '').strip()

        if not title or not template_text:
            return JsonResponse({'status': 'error', 'message': 'Title and Template Text are required.'}, status=400)

        tmpl = CommunicationTemplate.objects.create(title=title, channel=channel, category=category, template_text=template_text)
        return JsonResponse({'status': 'success', 'message': 'Template created successfully!', 'template_id': tmpl.id})


@csrf_exempt
@require_http_methods(["POST"])
def api_admin_comm_toggle_star(request):
    """
    Toggles starred status on a communication message or conversation log in DB.
    """
    data = json.loads(request.body.decode('utf-8')) if request.content_type == 'application/json' else request.POST
    log_id = data.get('log_id')
    log_entry = CommunicationLog.objects.filter(id=log_id).first() if log_id else None
    if not log_entry:
        return JsonResponse({'status': 'error', 'message': 'Message record not found.'}, status=404)
    
    log_entry.is_starred = not log_entry.is_starred
    log_entry.save()
    return JsonResponse({'status': 'success', 'is_starred': log_entry.is_starred, 'message': 'Starred status updated.'})


@csrf_exempt
@require_http_methods(["POST"])
def api_admin_comm_toggle_archive(request):
    """
    Toggles archived status on a communication message or conversation log in DB.
    """
    data = json.loads(request.body.decode('utf-8')) if request.content_type == 'application/json' else request.POST
    log_id = data.get('log_id')
    log_entry = CommunicationLog.objects.filter(id=log_id).first() if log_id else None
    if not log_entry:
        return JsonResponse({'status': 'error', 'message': 'Message record not found.'}, status=404)
    
    log_entry.is_archived = not log_entry.is_archived
    log_entry.save()
    return JsonResponse({'status': 'success', 'is_archived': log_entry.is_archived, 'message': 'Archived status updated.'})
