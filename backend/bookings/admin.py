from django.contrib import admin
from .models import FreeTrialBooking, Teacher


@admin.register(FreeTrialBooking)
class FreeTrialBookingAdmin(admin.ModelAdmin):
    list_display = (
        'booking_id', 'student_name', 'student_mobile', 'student_email',
        'student_class', 'subject', 'tuition_mode', 'assigned_teacher',
        'tutor_name', 'preferred_demo_date', 'booking_status', 'created_at'
    )

    search_fields = (
        'booking_id', 'student_name', 'student_mobile',
        'student_email', 'tutor_name', 'assigned_teacher__full_name',
        'assigned_teacher__teacher_id'
    )

    list_filter = (
        'booking_status', 'tuition_mode',
        'preferred_demo_date', 'created_at'
    )

    actions = [
        'approve_bookings',
        'mark_scheduled',
        'mark_completed',
        'mark_followup',
        'reject_bookings',
        'cancel_bookings'
    ]

    def approve_bookings(self, request, queryset):
        queryset.update(booking_status='Approved')
    approve_bookings.short_description = "Approve selected bookings"

    def mark_scheduled(self, request, queryset):
        queryset.update(booking_status='Scheduled')
    mark_scheduled.short_description = "Mark selected as Scheduled"

    def mark_completed(self, request, queryset):
        queryset.update(booking_status='Completed')
    mark_completed.short_description = "Mark selected as Completed"

    def mark_followup(self, request, queryset):
        queryset.update(booking_status='Follow-Up')
    mark_followup.short_description = "Mark selected for Follow-Up"

    def reject_bookings(self, request, queryset):
        queryset.update(booking_status='Rejected')
    reject_bookings.short_description = "Reject selected bookings"

    def cancel_bookings(self, request, queryset):
        queryset.update(booking_status='Cancelled')
    cancel_bookings.short_description = "Cancel selected bookings"


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = (
        'teacher_id',
        'full_name',
        'email',
        'mobile',
        'city',
        'state',
        'verification_status',
        'registration_date',
    )

    search_fields = (
        'teacher_id',
        'full_name',
        'email',
        'mobile',
    )

    list_filter = (
        'verification_status',
        'city',
        'state',
    )

    ordering = ('-registration_date',)