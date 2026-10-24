from django.contrib import admin
from .models import (
    TeacherProfile, StudentProfile, ContactEnquiry, StudentParentEnquiry,
    TuitionRequirement, ActivityLog, VisitorTracker, AdminNotification,
    StudyMaterial
)

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('teacher_id', 'full_name', 'email', 'mobile', 'city', 'experience', 'verification_status', 'created_at')
    list_filter = ('verification_status', 'account_status', 'city', 'created_at')
    search_fields = ('teacher_id', 'full_name', 'email', 'mobile', 'city', 'subjects')

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'full_name', 'email', 'mobile', 'student_class', 'city', 'created_at')
    search_fields = ('student_id', 'full_name', 'email', 'mobile', 'city')

@admin.register(ContactEnquiry)
class ContactEnquiryAdmin(admin.ModelAdmin):
    list_display = ('enquiry_id', 'name', 'email', 'mobile', 'subject', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('enquiry_id', 'name', 'email', 'mobile', 'subject', 'message')

@admin.register(TuitionRequirement)
class TuitionRequirementAdmin(admin.ModelAdmin):
    list_display = ('requirement_id', 'student_name', 'student_class', 'subject', 'location', 'budget', 'status', 'created_at')
    list_filter = ('status', 'tuition_mode', 'created_at')
    search_fields = ('requirement_id', 'student_name', 'student_class', 'subject', 'location')

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('activity_type', 'user_name', 'user_role', 'description', 'page_url', 'ip_address', 'created_at')
    list_filter = ('activity_type', 'user_role', 'created_at')
    search_fields = ('user_name', 'description', 'page_url', 'ip_address')

@admin.register(VisitorTracker)
class VisitorTrackerAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'page_visited', 'visit_date', 'last_seen')
    list_filter = ('visit_date',)

@admin.register(AdminNotification)
class AdminNotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_read', 'created_at')
    list_filter = ('is_read', 'category', 'created_at')


@admin.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):
    list_display = ('material_id', 'title', 'class_name', 'subject', 'chapter', 'unit', 'status', 'download_count', 'created_at')
    list_filter = ('class_name', 'status', 'visibility', 'download_permission', 'featured', 'created_at')
    search_fields = ('material_id', 'title', 'subject', 'chapter', 'unit', 'keywords')



# Register LiveClass model in Django Admin with real-time date, teacher, status, and timestamps
from .models import LiveClass

@admin.register(LiveClass)
class LiveClassAdmin(admin.ModelAdmin):
    list_display = (
        'live_class_id', 
        'title', 
        'class_name', 
        'subject', 
        'teacher_name', 
        'schedule_date', 
        'schedule_time', 
        'status', 
        'created_at', 
        'updated_at'
    )
    list_filter = ('status', 'class_name', 'subject', 'schedule_date', 'created_at')
    search_fields = ('live_class_id', 'title', 'teacher_name', 'class_name', 'subject')
    ordering = ('-id',)
    readonly_fields = ('live_class_id', 'created_at', 'updated_at')


@admin.register(StudentParentEnquiry)
class StudentParentEnquiryAdmin(admin.ModelAdmin):
    list_display = ('enquiry_id', 'full_name', 'email', 'mobile', 'student_class', 'subject', 'city', 'source', 'status', 'created_at')
    list_filter = ('source', 'status', 'city', 'student_class', 'created_at')
    search_fields = ('enquiry_id', 'full_name', 'email', 'mobile', 'city', 'subject', 'student_class')


from .models import TeacherJobApplication, TeacherEnquiry, BusinessIDSequence

@admin.register(TeacherJobApplication)
class TeacherJobApplicationAdmin(admin.ModelAdmin):
    list_display = ('application_id', 'job_id', 'job_title', 'applicant_name', 'mobile', 'email', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('application_id', 'job_id', 'job_title', 'applicant_name', 'email', 'mobile')


@admin.register(TeacherEnquiry)
class TeacherEnquiryAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'mobile', 'qualification', 'city', 'status', 'created_at')
    list_filter = ('status', 'city', 'created_at')
    search_fields = ('full_name', 'email', 'mobile', 'city', 'subjects')


@admin.register(BusinessIDSequence)
class BusinessIDSequenceAdmin(admin.ModelAdmin):
    list_display = ('name', 'prefix', 'last_number', 'updated_at')
    readonly_fields = ('updated_at',)


from .models import CourseBatch, BatchTeacherAssignment, BatchCoupon, BatchActivityLog

@admin.register(CourseBatch)
class CourseBatchAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'title', 'class_name', 'board', 'stream', 'subject', 'status', 'batch_type', 'visibility', 'price', 'created_at')
    list_filter = ('class_name', 'board', 'stream', 'status', 'batch_type', 'visibility', 'created_at')
    search_fields = ('course_id', 'title', 'class_name', 'subject', 'board', 'stream')

@admin.register(BatchTeacherAssignment)
class BatchTeacherAssignmentAdmin(admin.ModelAdmin):
    list_display = ('batch', 'teacher', 'role_or_subject', 'assigned_at')
    list_filter = ('assigned_at',)
    search_fields = ('batch__title', 'teacher__full_name', 'role_or_subject')

@admin.register(BatchCoupon)
class BatchCouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'batch', 'discount_type', 'discount_value', 'is_active', 'used_count', 'usage_limit', 'created_at')
    list_filter = ('is_active', 'discount_type', 'created_at')
    search_fields = ('code', 'batch__title')

@admin.register(BatchActivityLog)
class BatchActivityLogAdmin(admin.ModelAdmin):
    list_display = ('batch', 'action', 'user_name', 'user_role', 'description', 'created_at')
    list_filter = ('action', 'user_role', 'created_at')
    search_fields = ('batch__title', 'user_name', 'description', 'action')

