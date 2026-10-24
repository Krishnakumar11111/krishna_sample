from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
import json
import os
import datetime
import re

from .models import AdminRole, UserRoleAssignment, PermissionAuditLog, StudentProfile, TeacherProfile

DEFAULT_SYSTEM_ROLES = [
    {
        'name': 'Super Admin',
        'code': 'super_admin',
        'type': 'System',
        'desc': 'Full system control with unrestricted access across all modules, settings, security, and financial operations.',
        'permissions': {
            'users': {'view': True, 'create': True, 'edit': True, 'delete': True, 'approve': True, 'export': True, 'import': True, 'settings': True},
            'academics': {'view': True, 'create': True, 'edit': True, 'delete': True, 'approve': True, 'export': True, 'import': True, 'settings': True},
            'content': {'view': True, 'create': True, 'edit': True, 'delete': True, 'approve': True, 'export': True, 'import': True, 'settings': True},
            'live_classes': {'view': True, 'create': True, 'edit': True, 'delete': True, 'approve': True, 'export': True, 'import': True, 'settings': True},
            'examinations': {'view': True, 'create': True, 'edit': True, 'delete': True, 'approve': True, 'export': True, 'import': True, 'settings': True},
            'assignments': {'view': True, 'create': True, 'edit': True, 'delete': True, 'approve': True, 'export': True, 'import': True, 'settings': True},
            'attendance': {'view': True, 'create': True, 'edit': True, 'delete': True, 'approve': True, 'export': True, 'import': True, 'settings': True},
            'certificates': {'view': True, 'create': True, 'edit': True, 'delete': True, 'approve': True, 'export': True, 'import': True, 'settings': True},
            'payments': {'view': True, 'create': True, 'edit': True, 'delete': True, 'approve': True, 'export': True, 'import': True, 'settings': True},
            'reports': {'view': True, 'create': True, 'edit': True, 'delete': True, 'approve': True, 'export': True, 'import': True, 'settings': True},
            'communication': {'view': True, 'create': True, 'edit': True, 'delete': True, 'approve': True, 'export': True, 'import': True, 'settings': True},
            'coupons': {'view': True, 'create': True, 'edit': True, 'delete': True, 'approve': True, 'export': True, 'import': True, 'settings': True},
            'cms': {'view': True, 'create': True, 'edit': True, 'delete': True, 'approve': True, 'export': True, 'import': True, 'settings': True},
            'media': {'view': True, 'create': True, 'edit': True, 'delete': True, 'approve': True, 'export': True, 'import': True, 'settings': True},
            'system': {'view': True, 'create': True, 'edit': True, 'delete': True, 'approve': True, 'export': True, 'import': True, 'settings': True},
            'support': {'view': True, 'create': True, 'edit': True, 'delete': True, 'approve': True, 'export': True, 'import': True, 'settings': True}
        }
    },
    {
        'name': 'Admin',
        'code': 'admin',
        'type': 'System',
        'desc': 'Operational manager with access to academic, user, content, exam, and reporting features.',
        'permissions': {
            'users': {'view': True, 'create': True, 'edit': True, 'delete': False, 'approve': True, 'export': True, 'import': False, 'settings': False},
            'academics': {'view': True, 'create': True, 'edit': True, 'delete': False, 'approve': True, 'export': True, 'import': True, 'settings': False},
            'content': {'view': True, 'create': True, 'edit': True, 'delete': True, 'approve': True, 'export': True, 'import': True, 'settings': False},
            'live_classes': {'view': True, 'create': True, 'edit': True, 'delete': True, 'approve': True, 'export': True, 'import': False, 'settings': False},
            'examinations': {'view': True, 'create': True, 'edit': True, 'delete': True, 'approve': True, 'export': True, 'import': False, 'settings': False},
            'assignments': {'view': True, 'create': True, 'edit': True, 'delete': True, 'approve': True, 'export': True, 'import': False, 'settings': False},
            'attendance': {'view': True, 'create': True, 'edit': True, 'delete': False, 'approve': True, 'export': True, 'import': False, 'settings': False},
            'reports': {'view': True, 'create': False, 'edit': False, 'delete': False, 'approve': False, 'export': True, 'import': False, 'settings': False}
        }
    },
    {
        'name': 'Teacher',
        'code': 'teacher',
        'type': 'System',
        'desc': 'Faculty member managing live classes, lectures, assignments, tests, and student progress.',
        'permissions': {
            'academics': {'view': True, 'create': False, 'edit': False, 'delete': False, 'approve': False, 'export': False, 'import': False, 'settings': False},
            'content': {'view': True, 'create': True, 'edit': True, 'delete': False, 'approve': False, 'export': True, 'import': False, 'settings': False},
            'live_classes': {'view': True, 'create': True, 'edit': True, 'delete': False, 'approve': False, 'export': False, 'import': False, 'settings': False},
            'examinations': {'view': True, 'create': True, 'edit': True, 'delete': False, 'approve': False, 'export': True, 'import': False, 'settings': False},
            'assignments': {'view': True, 'create': True, 'edit': True, 'delete': False, 'approve': True, 'export': True, 'import': False, 'settings': False},
            'attendance': {'view': True, 'create': True, 'edit': True, 'delete': False, 'approve': False, 'export': True, 'import': False, 'settings': False}
        }
    },
    {
        'name': 'Student',
        'code': 'student',
        'type': 'System',
        'desc': 'Enrolled learner accessing live streams, recorded lectures, study notes, and exams.',
        'permissions': {
            'academics': {'view': True, 'create': False, 'edit': False, 'delete': False, 'approve': False, 'export': False, 'import': False, 'settings': False},
            'content': {'view': True, 'create': False, 'edit': False, 'delete': False, 'approve': False, 'export': False, 'import': False, 'settings': False},
            'live_classes': {'view': True, 'create': False, 'edit': False, 'delete': False, 'approve': False, 'export': False, 'import': False, 'settings': False},
            'examinations': {'view': True, 'create': False, 'edit': False, 'delete': False, 'approve': False, 'export': False, 'import': False, 'settings': False},
            'assignments': {'view': True, 'create': True, 'edit': False, 'delete': False, 'approve': False, 'export': False, 'import': False, 'settings': False}
        }
    },
    {
        'name': 'Accountant',
        'code': 'accountant',
        'type': 'Custom',
        'desc': 'Finance officer managing payment transactions, refunds, student invoices, and payout reports.',
        'permissions': {
            'payments': {'view': True, 'create': True, 'edit': True, 'delete': False, 'approve': True, 'export': True, 'import': False, 'settings': False},
            'reports': {'view': True, 'create': False, 'edit': False, 'delete': False, 'approve': False, 'export': True, 'import': False, 'settings': False}
        }
    },
    {
        'name': 'Academic Manager',
        'code': 'academic_manager',
        'type': 'Custom',
        'desc': 'Curriculum coordinator managing classes, subjects, courses, batches, and enrollments.',
        'permissions': {
            'academics': {'view': True, 'create': True, 'edit': True, 'delete': True, 'approve': True, 'export': True, 'import': True, 'settings': True},
            'content': {'view': True, 'create': True, 'edit': True, 'delete': True, 'approve': True, 'export': True, 'import': True, 'settings': False}
        }
    }
]


def _seed_system_roles_if_needed():
    try:
        for r_info in DEFAULT_SYSTEM_ROLES:
            role, created = AdminRole.objects.get_or_create(
                role_name=r_info['name'],
                defaults={
                    'role_code': r_info['code'],
                    'role_type': r_info['type'],
                    'description': r_info['desc'],
                    'status': 'Active',
                    'permissions_json': json.dumps(r_info['permissions'])
                }
            )
            if not created and not role.role_code:
                role.role_code = r_info['code']
                role.role_type = r_info['type']
                role.save()
    except Exception as e:
        print("Role seed exception:", e)


def _render_admin_module_response(request, module_name='roles_permissions'):
    if not (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)):
        import urllib.parse
        return redirect(f'/admin/login/?next={urllib.parse.quote(request.path)}')
    
    context_extra = {
        'base_template': 'admin_partial_base.html' if request.headers.get('x-requested-with') == 'XMLHttpRequest' else 'admin.html',
        'active_module': module_name
    }
    return render(request, 'admin/roles_permissions.html', context_extra)


def admin_roles_permissions_view(request):
    """
    Super Admin Roles & Permissions Control Center View Controller.
    """
    return _render_admin_module_response(request, 'roles_permissions')


# ==========================================
# REST API CONTROLLERS FOR ROLES & PERMISSIONS
# ==========================================

@csrf_exempt
def api_admin_roles_list_create(request):
    """
    GET: List all roles + dashboard summary stats.
    POST: Create a new custom role.
    """
    _seed_system_roles_if_needed()

    if request.method == 'GET':
        q = request.GET.get('q', '').strip()
        status_filter = request.GET.get('status', '')

        roles_qs = AdminRole.objects.all()

        if q:
            roles_qs = roles_qs.filter(role_name__icontains=q)
        if status_filter:
            roles_qs = roles_qs.filter(status=status_filter)

        role_list = []
        for r in roles_qs:
            user_count = UserRoleAssignment.objects.filter(role=r).count()
            if r.role_name == 'Super Admin':
                user_count = max(user_count, User.objects.filter(is_superuser=True).count())

            perm_dict = json.loads(r.permissions_json or '{}')
            total_active_perms = sum(1 for m in perm_dict.values() for p, val in m.items() if val)

            role_list.append({
                'id': r.id,
                'name': r.role_name,
                'code': r.role_code or re.sub(r'[^a-zA-Z0-9_]', '_', r.role_name.lower()),
                'type': r.role_type,
                'status': r.status,
                'description': r.description or 'No description provided.',
                'user_count': user_count,
                'permission_count': total_active_perms,
                'created_at': r.created_at.strftime('%d %b %Y')
            })

        # Summary statistics
        total_roles = AdminRole.objects.count()
        active_roles = AdminRole.objects.filter(status='Active').count()
        total_users = User.objects.count()
        custom_roles = AdminRole.objects.filter(role_type='Custom').count()
        recent_changes_count = PermissionAuditLog.objects.count()

        summary_stats = {
            'total_roles': total_roles,
            'active_roles': active_roles,
            'total_users': total_users,
            'custom_roles': custom_roles,
            'permission_groups': 16, # 16 Master Modules
            'recent_changes': recent_changes_count
        }

        return JsonResponse({
            'status': 'success',
            'summary': summary_stats,
            'roles': role_list
        })

    elif request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8')) if request.content_type == 'application/json' else request.POST
            name = data.get('role_name', '').strip()
            desc = data.get('description', '').strip()
            code = data.get('role_code', '').strip()

            if not name:
                return JsonResponse({'status': 'error', 'message': 'Role Name is required.'}, status=400)

            if not code:
                code = re.sub(r'[^a-zA-Z0-9_]', '_', name.lower())

            if AdminRole.objects.filter(role_name__iexact=name).exists():
                return JsonResponse({'status': 'error', 'message': f"A role named '{name}' already exists."}, status=400)

            if AdminRole.objects.filter(role_code__iexact=code).exists():
                return JsonResponse({'status': 'error', 'message': f"Role code '{code}' already exists."}, status=400)

            role = AdminRole.objects.create(
                role_name=name,
                role_code=code,
                description=desc,
                role_type='Custom',
                status='Active',
                permissions_json='{}'
            )

            # Log Audit Entry
            PermissionAuditLog.objects.create(
                admin_user=request.user.username if (request.user and request.user.is_authenticated) else 'Super Admin',
                role_name=role.role_name,
                module_name='Role Management',
                permission_key='create_role',
                old_value='--',
                new_value=role.role_name,
                action='CREATE'
            )

            return JsonResponse({
                'status': 'success',
                'message': f"Role '{role.role_name}' created successfully!",
                'role_id': role.id
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
def api_admin_role_detail_update_delete(request, role_id):
    """
    GET: Get full role permissions & details.
    PATCH: Update role permissions & metadata.
    DELETE: Delete custom role.
    """
    _seed_system_roles_if_needed()
    role = get_object_or_404(AdminRole, id=role_id)

    if request.method == 'GET':
        user_assignments = UserRoleAssignment.objects.filter(role=role).select_related('user')[:20]
        assigned_users_list = [{
            'id': u.user.id,
            'username': u.user.username,
            'email': u.user.email or 'N/A',
            'is_primary': u.is_primary,
            'assigned_at': u.assigned_at.strftime('%d %b %Y')
        } for u in user_assignments]

        audit_logs = PermissionAuditLog.objects.filter(role_name=role.role_name).order_by('-timestamp')[:10]
        audit_list = [{
            'admin_user': a.admin_user,
            'module': a.module_name,
            'permission': a.permission_key,
            'old_val': a.old_value,
            'new_val': a.new_value,
            'timestamp': a.timestamp.strftime('%d %b %Y, %I:%M %p')
        } for a in audit_logs]

        return JsonResponse({
            'status': 'success',
            'role': {
                'id': role.id,
                'name': role.role_name,
                'code': role.role_code,
                'type': role.role_type,
                'status': role.status,
                'description': role.description,
                'permissions': json.loads(role.permissions_json or '{}'),
                'created_at': role.created_at.strftime('%d %b %Y, %I:%M %p')
            },
            'assigned_users': assigned_users_list,
            'audit_logs': audit_list
        })

    elif request.method in ['PATCH', 'POST']:
        try:
            data = json.loads(request.body.decode('utf-8')) if request.content_type == 'application/json' else request.POST
            admin_user = request.user.username if (request.user and request.user.is_authenticated) else 'Super Admin'
            ip_addr = request.META.get('REMOTE_ADDR', '127.0.0.1')

            if 'role_name' in data and role.role_type != 'System':
                role.role_name = data['role_name']
            if 'description' in data:
                role.description = data['description']
            if 'permissions' in data:
                old_perms = role.permissions_json
                new_perms = json.dumps(data['permissions'])
                role.permissions_json = new_perms

                # Record Audit Log
                PermissionAuditLog.objects.create(
                    admin_user=admin_user,
                    role_name=role.role_name,
                    module_name='Permission Matrix',
                    permission_key='matrix_update',
                    old_value='Previous Permissions',
                    new_value='Updated Matrix',
                    action='UPDATE',
                    ip_address=ip_addr
                )

            role.updated_by = admin_user
            role.save()

            return JsonResponse({
                'status': 'success',
                'message': f"Permissions for role '{role.role_name}' saved successfully!"
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    elif request.method == 'DELETE':
        if role.role_type == 'System':
            return JsonResponse({'status': 'error', 'message': 'System roles cannot be deleted.'}, status=400)

        assigned_count = UserRoleAssignment.objects.filter(role=role).count()
        if assigned_count > 0:
            return JsonResponse({'status': 'error', 'message': f"Cannot delete role. {assigned_count} users are currently assigned to this role. Reassign them first."}, status=400)

        r_name = role.role_name
        role.delete()

        PermissionAuditLog.objects.create(
            admin_user=request.user.username if (request.user and request.user.is_authenticated) else 'Super Admin',
            role_name=r_name,
            module_name='Role Management',
            permission_key='delete_role',
            old_value=r_name,
            new_value='Deleted',
            action='DELETE'
        )

        return JsonResponse({
            'status': 'success',
            'message': f"Custom role '{r_name}' deleted successfully!"
        })


@csrf_exempt
@require_http_methods(["POST"])
def api_admin_role_duplicate(request, role_id):
    """
    Duplicates an existing role into a new custom role.
    """
    try:
        source_role = get_object_or_404(AdminRole, id=role_id)
        new_name = f"{source_role.role_name} (Copy)"
        counter = 1
        while AdminRole.objects.filter(role_name=new_name).exists():
            counter += 1
            new_name = f"{source_role.role_name} (Copy {counter})"

        new_code = re.sub(r'[^a-zA-Z0-9_]', '_', new_name.lower())

        new_role = AdminRole.objects.create(
            role_name=new_name,
            role_code=new_code,
            description=f"Duplicated from {source_role.role_name}.",
            role_type='Custom',
            status='Active',
            permissions_json=source_role.permissions_json
        )

        PermissionAuditLog.objects.create(
            admin_user=request.user.username if (request.user and request.user.is_authenticated) else 'Super Admin',
            role_name=new_role.role_name,
            module_name='Role Management',
            permission_key='duplicate_role',
            old_value=source_role.role_name,
            new_value=new_role.role_name,
            action='CREATE'
        )

        return JsonResponse({
            'status': 'success',
            'message': f"Role '{new_name}' duplicated successfully!",
            'new_role_id': new_role.id
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_admin_role_toggle_status(request, role_id):
    """
    Toggles role status between Active and Inactive.
    """
    try:
        role = get_object_or_404(AdminRole, id=role_id)
        if role.role_name == 'Super Admin':
            return JsonResponse({'status': 'error', 'message': 'Super Admin role status cannot be deactivated.'}, status=400)

        role.status = 'Inactive' if role.status == 'Active' else 'Active'
        role.save()

        PermissionAuditLog.objects.create(
            admin_user=request.user.username if (request.user and request.user.is_authenticated) else 'Super Admin',
            role_name=role.role_name,
            module_name='Role Management',
            permission_key='toggle_status',
            old_value='Inactive' if role.status == 'Active' else 'Active',
            new_value=role.status,
            action='UPDATE'
        )

        return JsonResponse({
            'status': 'success',
            'message': f"Role '{role.role_name}' status set to {role.status}."
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
def api_admin_role_users(request, role_id):
    """
    GET: List users assigned to a role.
    POST: Assign a user to a role.
    """
    role = get_object_or_404(AdminRole, id=role_id)

    if request.method == 'GET':
        assignments = UserRoleAssignment.objects.filter(role=role).select_related('user')
        u_list = [{
            'id': a.user.id,
            'username': a.user.username,
            'email': a.user.email or 'N/A',
            'is_primary': a.is_primary,
            'assigned_by': a.assigned_by,
            'assigned_at': a.assigned_at.strftime('%d %b %Y')
        } for a in assignments]
        return JsonResponse({'status': 'success', 'users': u_list})

    elif request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8')) if request.content_type == 'application/json' else request.POST
            username = data.get('username', '').strip()
            user = User.objects.filter(username__iexact=username).first()

            if not user:
                return JsonResponse({'status': 'error', 'message': f"User '{username}' not found."}, status=404)

            assignment, created = UserRoleAssignment.objects.get_or_create(
                user=user,
                role=role,
                defaults={'assigned_by': request.user.username if (request.user and request.user.is_authenticated) else 'Super Admin'}
            )

            if not created:
                return JsonResponse({'status': 'error', 'message': f"User '{username}' is already assigned to this role."}, status=400)

            PermissionAuditLog.objects.create(
                admin_user=request.user.username if (request.user and request.user.is_authenticated) else 'Super Admin',
                role_name=role.role_name,
                module_name='Role Assignment',
                permission_key='assign_user',
                old_value='--',
                new_value=user.username,
                action='CREATE'
            )

            return JsonResponse({
                'status': 'success',
                'message': f"User '{user.username}' successfully assigned to '{role.role_name}'!"
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def api_admin_role_user_remove(request, role_id, user_id):
    """
    Removes user assignment from a role.
    """
    try:
        role = get_object_or_404(AdminRole, id=role_id)
        user = get_object_or_404(User, id=user_id)

        assignment = UserRoleAssignment.objects.filter(role=role, user=user).first()
        if assignment:
            assignment.delete()

        PermissionAuditLog.objects.create(
            admin_user=request.user.username if (request.user and request.user.is_authenticated) else 'Super Admin',
            role_name=role.role_name,
            module_name='Role Assignment',
            permission_key='remove_user',
            old_value=user.username,
            new_value='Removed',
            action='DELETE'
        )

        return JsonResponse({
            'status': 'success',
            'message': f"User '{user.username}' removed from role '{role.role_name}'."
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_admin_roles_compare(request):
    """
    Compares 2-4 selected roles side-by-side.
    """
    try:
        data = json.loads(request.body.decode('utf-8')) if request.content_type == 'application/json' else request.POST
        role_ids = data.get('role_ids', [])

        if not role_ids or len(role_ids) < 2:
            return JsonResponse({'status': 'error', 'message': 'Select at least 2 roles to compare.'}, status=400)

        roles = AdminRole.objects.filter(id__in=role_ids)
        comparison = []

        modules = ['users', 'academics', 'content', 'live_classes', 'examinations', 'assignments', 'attendance', 'certificates', 'payments', 'reports', 'communication', 'coupons', 'cms', 'media', 'system', 'support']
        actions = ['view', 'create', 'edit', 'delete', 'approve', 'export']

        for m in modules:
            for act in actions:
                row = {'module': m.upper(), 'action': act.upper(), 'roles': {}}
                for r in roles:
                    p_dict = json.loads(r.permissions_json or '{}')
                    val = p_dict.get(m, {}).get(act, False)
                    row['roles'][r.role_name] = val
                comparison.append(row)

        return JsonResponse({
            'status': 'success',
            'roles': [r.role_name for r in roles],
            'comparison': comparison
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
def api_admin_roles_audit_logs(request):
    """
    Returns permission audit logs history.
    """
    logs = PermissionAuditLog.objects.order_by('-timestamp')[:30]
    log_list = [{
        'id': l.id,
        'admin_user': l.admin_user,
        'role_name': l.role_name,
        'module_name': l.module_name,
        'permission_key': l.permission_key,
        'old_value': l.old_value or '--',
        'new_value': l.new_value or '--',
        'action': l.action,
        'timestamp': l.timestamp.strftime('%d %b %Y, %I:%M %p')
    } for l in logs]

    return JsonResponse({'status': 'success', 'audit_logs': log_list})
