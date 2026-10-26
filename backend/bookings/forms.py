from django import forms
from .models import FreeTrialBooking

class FreeTrialBookingForm(forms.ModelForm):
    class Meta:
        model = FreeTrialBooking
        fields = [
            'booking_status', 'student_name', 'parent_name', 'student_mobile',
            'student_email', 'student_gender', 'student_class', 'board', 'subject',
            'assigned_teacher', 'tutor_name', 'tutor_photo', 'tutor_rating',
            'tutor_qualification', 'tutor_experience', 'tutor_location', 'tutor_mode',
            'demo_type', 'tuition_mode', 'preferred_demo_date', 'preferred_time_slot',
            'scheduled_datetime', 'number_of_demo_sessions', 'preferred_language',
            'learning_goal', 'additional_notes', 'rejection_reason', 'followup_status',
            'followup_notes', 'state', 'city', 'locality', 'landmark', 'complete_address'
        ]