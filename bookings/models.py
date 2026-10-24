from django.db import models
from django.utils.crypto import get_random_string
import random

class FreeTrialBooking(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Teacher Assigned', 'Teacher Assigned'),
        ('Scheduled', 'Scheduled'),
        ('Live', 'Live'),
        ('Completed', 'Completed'),
        ('Follow-Up', 'Follow-Up'),
        ('Interested', 'Interested'),
        ('Not Interested', 'Not Interested'),
        ('Closed', 'Closed'),
        ('Rejected', 'Rejected'),
        ('Cancelled', 'Cancelled'),
    ]

    # Booking Information
    booking_id = models.CharField(max_length=50, unique=True, blank=True, db_index=True)
    booking_status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')

    # Student & Parent Information
    student_name = models.CharField(max_length=150)
    parent_name = models.CharField(max_length=150, blank=True, null=True)
    student_mobile = models.CharField(max_length=15)
    student_email = models.EmailField()
    student_gender = models.CharField(max_length=50, blank=True, null=True)
    student_class = models.CharField(max_length=50)
    board = models.CharField(max_length=100, blank=True, null=True)
    subject = models.CharField(max_length=100)

    # Tutor & Assignment Information
    tutor_id = models.CharField(max_length=50, blank=True, null=True)
    tutor_name = models.CharField(max_length=150, blank=True, null=True)
    assigned_teacher = models.ForeignKey('TutionPlatform.TeacherProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_demo_bookings')
    tutor_photo = models.URLField(max_length=500, blank=True, null=True)
    tutor_rating = models.CharField(max_length=10, blank=True, null=True)
    tutor_qualification = models.CharField(max_length=200, blank=True, null=True)
    tutor_experience = models.CharField(max_length=50, blank=True, null=True)
    tutor_location = models.CharField(max_length=150, blank=True, null=True)
    tutor_mode = models.CharField(max_length=100, blank=True, null=True)

    # Demo Details & Scheduling
    demo_type = models.CharField(max_length=100, blank=True, null=True, default='Online / Home Demo')
    tuition_mode = models.CharField(max_length=100)
    preferred_demo_date = models.DateField(blank=True, null=True)
    preferred_time_slot = models.CharField(max_length=100, blank=True, null=True)
    scheduled_datetime = models.DateTimeField(blank=True, null=True)
    number_of_demo_sessions = models.IntegerField(default=1)
    preferred_language = models.CharField(max_length=100, blank=True, null=True)
    learning_goal = models.CharField(max_length=255, blank=True, null=True)
    additional_notes = models.TextField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    followup_status = models.CharField(max_length=50, blank=True, null=True)
    followup_notes = models.TextField(blank=True, null=True)

    # Address (For Home Tuition)
    state = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    locality = models.CharField(max_length=150, blank=True, null=True)
    landmark = models.CharField(max_length=150, blank=True, null=True)
    complete_address = models.TextField(blank=True, null=True)

    # System Information
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    browser = models.CharField(max_length=255, blank=True, null=True)
    operating_system = models.CharField(max_length=255, blank=True, null=True)
    device_type = models.CharField(max_length=100, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.booking_id:
            from TutionPlatform.models import BusinessIDSequence
            self.booking_id = BusinessIDSequence.get_next_id('DEMO')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.booking_id} - {self.student_name}"

   
class Teacher(models.Model):
    """
    Legacy Teacher model.
    Note: The active teacher profile used by registrations and admin approval is TutionPlatform.models.TeacherProfile.
    """
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Suspended', 'Suspended'),
    ]
    teacher_id = models.CharField(max_length=15, unique=True, editable=False)
    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=20)
    experience = models.CharField(max_length=50)
    mobile = models.CharField(max_length=10, unique=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=6, blank=True, null=True)
    teaching_classes = models.TextField()
    subjects = models.TextField()
    expected_fee = models.CharField(max_length=100)
    bio = models.TextField(blank=True, null=True)
    profile_photo = models.ImageField(upload_to='teachers/photos/', blank=True, null=True)
    
    verification_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    registration_date = models.DateTimeField(auto_now_add=True)
    device_info = models.CharField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.teacher_id:
            self.teacher_id = f"EDUT-{get_random_string(6).upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} ({self.teacher_id})"