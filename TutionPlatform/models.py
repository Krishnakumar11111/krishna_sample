import os
import random
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator

def study_material_upload_path(instance, filename):
    cls_slug = slugify(instance.class_name or "general").replace('-', '_')
    subj_slug = slugify(instance.subject or "general").replace('-', '_')
    chap_slug = slugify(instance.chapter or "general").replace('-', '_')
    name, ext = os.path.splitext(filename)
    safe_name = slugify(name)
    if not safe_name:
        safe_name = "pdf_document"
    final_filename = f"{safe_name}{ext.lower()}"
    return os.path.join('study_material', cls_slug, subj_slug, chap_slug, final_filename)

def study_material_thumbnail_path(instance, filename):
    cls_slug = slugify(instance.class_name or "general").replace('-', '_')
    name, ext = os.path.splitext(filename)
    safe_name = slugify(name)
    return os.path.join('study_material', cls_slug, 'thumbnails', f"{safe_name}{ext.lower()}")

class TeacherProfile(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    EXPERIENCE_CHOICES = [
        ('Fresher', 'Fresher'),
        ('1 Year', '1 Year'),
        ('2 Years', '2 Years'),
        ('3 Years', '3 Years'),
        ('5+ Years', '5+ Years'),
        ('10+ Years', '10+ Years'),
    ]

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Suspended', 'Suspended'),
        ('Inactive', 'Inactive'),
    ]

    VERIFICATION_CHOICES = [
        ('Pending Approval', 'Pending Approval'),
        ('Under Review', 'Under Review'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Suspended', 'Suspended'),
        ('Deleted', 'Deleted'),
    ]

    teacher_id = models.CharField(max_length=20, unique=True, blank=True)
    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    experience = models.CharField(max_length=50, choices=EXPERIENCE_CHOICES)
    qualification = models.CharField(max_length=255, blank=True, null=True, default="Graduate")
    
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10, blank=True, null=True)

    teaching_classes = models.TextField()
    subjects = models.TextField()
    expected_fee = models.CharField(max_length=100)
    tuition_mode = models.CharField(max_length=100, default="Home & Online Tuition")
    languages = models.CharField(max_length=150, default="English, Hindi")

    bio = models.TextField(blank=True, null=True)
    profile_photo = models.ImageField(upload_to='teacher_photos/', blank=True, null=True)

    designation = models.CharField(max_length=150, blank=True, null=True, default="Senior Faculty")
    dob = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    university = models.CharField(max_length=200, blank=True, null=True)
    degree = models.CharField(max_length=150, blank=True, null=True)
    specialization = models.CharField(max_length=200, blank=True, null=True)
    certifications = models.TextField(blank=True, null=True)
    previous_experience = models.TextField(blank=True, null=True)
    employee_type = models.CharField(max_length=50, blank=True, null=True, default="Full-Time Faculty")
    department = models.CharField(max_length=100, blank=True, null=True, default="Academics")

    rating = models.FloatField(default=5.0)
    total_reviews = models.IntegerField(default=1)

    account_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_CHOICES, default='Pending Approval')
    
    approved = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)

    registration_date = models.DateField(auto_now_add=True, null=True, blank=True)
    registration_time = models.TimeField(auto_now_add=True, null=True, blank=True)
    registration_day = models.CharField(max_length=20, blank=True, null=True)
    registration_month = models.CharField(max_length=20, blank=True, null=True)
    registration_year = models.CharField(max_length=10, blank=True, null=True)
    
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    browser = models.CharField(max_length=255, blank=True, null=True)
    device_type = models.CharField(max_length=100, blank=True, null=True)

    approval_date = models.DateTimeField(blank=True, null=True)
    approved_date = models.DateField(blank=True, null=True)
    approved_time = models.TimeField(blank=True, null=True)
    approved_by = models.CharField(max_length=150, blank=True, null=True)

    rejected_date = models.DateField(blank=True, null=True)
    rejected_time = models.TimeField(blank=True, null=True)
    rejected_by = models.CharField(max_length=150, blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.teacher_id:
            last_teacher = TeacherProfile.objects.filter(teacher_id__startswith='TUT-').order_by('-id').first()
            if last_teacher and last_teacher.teacher_id:
                try:
                    last_num = int(last_teacher.teacher_id.split('-')[1])
                    new_num = last_num + 1
                except Exception:
                    new_num = TeacherProfile.objects.count() + 1
            else:
                new_num = TeacherProfile.objects.count() + 1
            self.teacher_id = f"TUT-{new_num:03d}"
            while TeacherProfile.objects.filter(teacher_id=self.teacher_id).exists():
                new_num += 1
                self.teacher_id = f"TUT-{new_num:03d}"
        
        now = timezone.now()
        if not self.registration_day:
            self.registration_day = now.strftime('%A')
        if not self.registration_month:
            self.registration_month = now.strftime('%B')
        if not self.registration_year:
            self.registration_year = now.strftime('%Y')

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.teacher_id} - {self.full_name} ({self.verification_status})"


class TeacherProfileChangeLog(models.Model):
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name='change_logs')
    update_reference = models.CharField(max_length=50)  # e.g. UPD-10245
    field_name = models.CharField(max_length=100)       # e.g. mobile
    field_label = models.CharField(max_length=100)      # e.g. Mobile Number
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)
    changed_by = models.CharField(max_length=150, default='Teacher') # Teacher, Admin
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=30, default='Updated')      # Updated, Pending, Approved
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.update_reference} - {self.teacher.full_name} ({self.field_label})"


class StudentProfile(models.Model):
    student_id = models.CharField(max_length=20, unique=True, blank=True)
    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=50, blank=True, null=True)
    student_class = models.CharField(max_length=50, blank=True, null=True)
    board = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    
    dob = models.CharField(max_length=50, blank=True, null=True)
    father_name = models.CharField(max_length=150, blank=True, null=True)
    mother_name = models.CharField(max_length=150, blank=True, null=True)
    guardian_name = models.CharField(max_length=150, blank=True, null=True)
    guardian_mobile = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    school_name = models.CharField(max_length=200, blank=True, null=True)
    photo_url = models.CharField(max_length=500, blank=True, null=True)
    profile_photo = models.ImageField(upload_to='student_profiles/', blank=True, null=True)
    roll_number = models.CharField(max_length=50, blank=True, null=True)

    account_status = models.CharField(max_length=20, default='Active')

    ip_address = models.GenericIPAddressField(blank=True, null=True)
    browser = models.CharField(max_length=255, blank=True, null=True)
    device_type = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.student_id:
            self.student_id = f"STU-{random.randint(100000, 999999)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student_id} - {self.full_name}"


class StudentProfileChangeLog(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='change_logs')
    update_reference = models.CharField(max_length=50)  # e.g. UPD-10245
    field_name = models.CharField(max_length=100)       # e.g. mobile
    field_label = models.CharField(max_length=100)      # e.g. Mobile Number
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)
    changed_by = models.CharField(max_length=150, default='Student') # Student, Admin
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=30, default='Updated')      # Updated, Pending, Approved
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.update_reference} - {self.student.full_name} ({self.field_label})"


class ContactEnquiry(models.Model):
    enquiry_id = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=150)
    email = models.EmailField()
    mobile = models.CharField(max_length=15)
    subject = models.CharField(max_length=200, blank=True, null=True)
    message = models.TextField()
    status = models.CharField(max_length=20, default='Pending') # Pending, Replied, Closed
    reply_message = models.TextField(blank=True, null=True)

    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.enquiry_id:
            self.enquiry_id = f"ENQ-{random.randint(100000, 999999)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.enquiry_id} - {self.name} ({self.status})"


class TuitionRequirement(models.Model):
    requirement_id = models.CharField(max_length=20, unique=True, blank=True)
    student_name = models.CharField(max_length=150)
    student_mobile = models.CharField(max_length=15)
    student_email = models.EmailField(blank=True, null=True)
    student_class = models.CharField(max_length=50)
    subject = models.CharField(max_length=150)
    budget = models.CharField(max_length=100)
    location = models.CharField(max_length=150)
    preferred_timing = models.CharField(max_length=100, blank=True, null=True)
    tuition_mode = models.CharField(max_length=100, default='Home Tuition')
    status = models.CharField(max_length=20, default='Open') # Open, Assigned, Closed

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.requirement_id:
            self.requirement_id = f"REQ-{random.randint(100000, 999999)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.requirement_id} - {self.subject} ({self.student_class})"


class JobApplication(models.Model):
    """Stores applications submitted by teachers/users from the home page Apply Now button."""
    application_id = models.CharField(max_length=20, unique=True, blank=True)
    job_id = models.CharField(max_length=50)  # requirement_id or booking_id of the job applied for
    job_title = models.CharField(max_length=255)  # Display title e.g. "Class 10 - Mathematics"
    applicant_name = models.CharField(max_length=150)
    mobile = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=30, default='Pending', choices=[
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Suspended', 'Suspended'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.application_id:
            self.application_id = f"APP-{random.randint(100000, 999999)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.application_id} - {self.applicant_name} ({self.status})"


class UserAuthLog(models.Model):
    ACTIVITY_CHOICES = [
        ('REGISTRATION', 'Registration'),
        ('LOGIN', 'Login'),
        ('FAILED_LOGIN', 'Failed Login'),
        ('LOGOUT', 'Logout'),
    ]
    STATUS_CHOICES = [
        ('Successful', 'Successful'),
        ('Failed', 'Failed'),
    ]
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='auth_logs')
    student_profile = models.ForeignKey('StudentProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='auth_logs')
    teacher_profile = models.ForeignKey('TeacherProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='auth_logs')
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_CHOICES)
    user_id_str = models.CharField(max_length=50, blank=True, null=True)
    full_name = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField()
    mobile = models.CharField(max_length=20, blank=True, null=True)
    user_role = models.CharField(max_length=50, default='Student') # Student, Tutor, Super Admin
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Successful')
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    device = models.CharField(max_length=50, blank=True, null=True) # Desktop, Mobile, Tablet
    browser = models.CharField(max_length=100, blank=True, null=True) # Chrome, Firefox, Safari, Edge
    operating_system = models.CharField(max_length=100, blank=True, null=True) # Windows, Android, iOS, macOS, Linux
    source_page = models.CharField(max_length=255, blank=True, null=True) # e.g. Login Form, Registration Form, Apply Popup
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.activity_type}] {self.email} ({self.status}) - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"


class ActivityLog(models.Model):
    activity_type = models.CharField(max_length=100) # e.g. Teacher Registered, Student Registered, Demo Booked, Page Visit, etc.
    user_name = models.CharField(max_length=150, default='Visitor')
    user_role = models.CharField(max_length=50, default='Visitor') # Teacher, Student, Visitor, Super Admin
    description = models.TextField()
    page_url = models.CharField(max_length=255, blank=True, null=True)
    
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    browser = models.CharField(max_length=255, blank=True, null=True)
    device_type = models.CharField(max_length=100, blank=True, null=True)
    
    day = models.CharField(max_length=20, blank=True, null=True)
    month = models.CharField(max_length=20, blank=True, null=True)
    year = models.CharField(max_length=10, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        now = timezone.now()
        if not self.day:
            self.day = now.strftime('%A')
        if not self.month:
            self.month = now.strftime('%B')
        if not self.year:
            self.year = now.strftime('%Y')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.activity_type}] {self.user_name} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"


class VisitorTracker(models.Model):
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    page_visited = models.CharField(max_length=255)
    browser = models.CharField(max_length=100, blank=True, null=True, default='Chrome')
    device_type = models.CharField(max_length=50, blank=True, null=True, default='Desktop')
    page_views = models.PositiveIntegerField(default=1)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True, default='India')
    last_seen = models.DateTimeField(auto_now=True)
    visit_date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-last_seen']

    def __str__(self):
        return f"{self.ip_address} - {self.page_visited} ({self.visit_date})"


class AdminNotification(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    category = models.CharField(max_length=50, default='system')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"


class StudyMaterial(models.Model):
    CLASS_CHOICES = [
        ('Class 6', 'Class 6'),
        ('Class 7', 'Class 7'),
        ('Class 8', 'Class 8'),
        ('Class 9', 'Class 9'),
        ('Class 10', 'Class 10'),
        ('Class 11', 'Class 11'),
        ('Class 12', 'Class 12'),
    ]

    VISIBILITY_CHOICES = [
        ('Public', 'Public'),
        ('Registered Users Only', 'Registered Users Only'),
    ]

    PERMISSION_CHOICES = [
        ('Free Download', 'Free Download'),
        ('Login Required', 'Login Required'),
    ]

    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Published', 'Published'),
        ('Deleted', 'Deleted'),
    ]

    content_type = models.CharField(max_length=50, default='study_material')
    material_id = models.CharField(max_length=20, unique=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    class_name = models.CharField(max_length=50, choices=CLASS_CHOICES)
    subject = models.CharField(max_length=100)
    chapter = models.CharField(max_length=150)
    unit = models.CharField(max_length=150)
    keywords = models.CharField(max_length=255, blank=True, null=True)
    
    pdf_file = models.FileField(
        upload_to=study_material_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )
    file_size = models.CharField(max_length=50, blank=True, null=True)
    thumbnail = models.ImageField(upload_to=study_material_thumbnail_path, blank=True, null=True)

    visibility = models.CharField(max_length=30, choices=VISIBILITY_CHOICES, default='Public')
    download_permission = models.CharField(max_length=30, choices=PERMISSION_CHOICES, default='Free Download')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Published')
    featured = models.BooleanField(default=False)

    download_count = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    uploaded_by = models.CharField(max_length=150, default='Super Admin')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.material_id:
            self.material_id = f"PDF-{random.randint(100000, 999999)}"
        if self.pdf_file and hasattr(self.pdf_file, 'size') and self.pdf_file.size:
            size_bytes = self.pdf_file.size
            if size_bytes < 1024 * 1024:
                self.file_size = f"{round(size_bytes / 1024, 1)} KB"
            else:
                self.file_size = f"{round(size_bytes / (1024 * 1024), 1)} MB"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.class_name} - {self.subject})"


class OnlineTest(models.Model):
    TEST_TYPE_CHOICES = [
        ('Daily Test', 'Daily Test'),
        ('Live Test', 'Live Test'),
        ('Weekly Test', 'Weekly Test'),
        ('Monthly Test', 'Monthly Test'),
    ]

    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Published', 'Published'),
        ('Live', 'Live'),
        ('Completed', 'Completed'),
        ('Deleted', 'Deleted'),
    ]

    test_id = models.CharField(max_length=20, unique=True, blank=True)
    test_type = models.CharField(max_length=50, choices=TEST_TYPE_CHOICES, default='Daily Test')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    class_name = models.CharField(max_length=50)
    subject = models.CharField(max_length=100)
    chapter = models.CharField(max_length=150)
    unit = models.CharField(max_length=150)

    pdf_file = models.FileField(upload_to='test_pdfs/', blank=True, null=True)
    test_date = models.DateField(blank=True, null=True)
    test_time = models.CharField(max_length=50, blank=True, null=True)
    test_day = models.CharField(max_length=30, blank=True, null=True)
    duration_mins = models.PositiveIntegerField(default=30)
    
    marks_per_question = models.FloatField(default=1.0)
    negative_marking = models.FloatField(default=0.0)
    total_marks = models.PositiveIntegerField(default=10)
    passing_marks = models.PositiveIntegerField(default=4)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Published')

    uploaded_by = models.CharField(max_length=150, default='Super Admin')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.test_id:
            self.test_id = f"TST-{random.randint(100000, 999999)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.test_type} - {self.title} ({self.class_name} - {self.subject})"


class TestQuestion(models.Model):
    test = models.ForeignKey(OnlineTest, on_delete=models.CASCADE, related_name='questions')
    question_number = models.PositiveIntegerField(default=1)
    question_text = models.TextField()
    option_a = models.CharField(max_length=255, blank=True, null=True)
    option_b = models.CharField(max_length=255, blank=True, null=True)
    option_c = models.CharField(max_length=255, blank=True, null=True)
    option_d = models.CharField(max_length=255, blank=True, null=True)
    correct_option = models.CharField(max_length=10, blank=True, null=True)
    explanation = models.TextField(blank=True, null=True)
    marks = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['question_number']

    def __str__(self):
        return f"Q{self.question_number} for {self.test.test_id}"


class StudentTestResult(models.Model):
    attempt_id = models.CharField(max_length=20, unique=True, blank=True)
    student_name = models.CharField(max_length=150, default='Student')
    student_mobile = models.CharField(max_length=15, default='9999999999')
    student_email = models.EmailField(blank=True, null=True)
    test = models.ForeignKey(OnlineTest, on_delete=models.CASCADE, related_name='results')
    
    obtained_marks = models.FloatField(default=0.0)
    total_marks = models.FloatField(default=0.0)
    percentage = models.FloatField(default=0.0)
    
    total_questions = models.PositiveIntegerField(default=0)
    correct_answers = models.PositiveIntegerField(default=0)
    wrong_answers = models.PositiveIntegerField(default=0)
    unanswered = models.PositiveIntegerField(default=0)
    
    status = models.CharField(max_length=20, default='Passed') # Passed, Failed
    time_taken_seconds = models.PositiveIntegerField(default=0)
    answers_json = models.TextField(blank=True, null=True)
    
    attempted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-attempted_at']

    def save(self, *args, **kwargs):
        if not self.attempt_id:
            self.attempt_id = f"ATT-{random.randint(100000, 999999)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student_name} - {self.test.title} ({self.obtained_marks}/{self.total_marks})"


def recorded_video_upload_path(instance, filename):
    cls_slug = slugify(instance.class_name or "general").replace('-', '_')
    subj_slug = slugify(instance.subject or "general").replace('-', '_')
    name, ext = os.path.splitext(filename)
    safe_name = slugify(name)
    if not safe_name:
        safe_name = "lecture_video"
    final_filename = f"{safe_name}{ext.lower()}"
    return os.path.join('recorded_lectures', cls_slug, subj_slug, final_filename)


class LiveClass(models.Model):
    STATUS_CHOICES = [
        ('Scheduled', 'Scheduled'),
        ('Live', 'Live'),
        ('Ended', 'Ended'),
    ]
    
    live_class_id = models.CharField(max_length=20, unique=True, blank=True)
    room_id = models.CharField(max_length=100, blank=True, null=True)
    title = models.CharField(max_length=300)
    class_name = models.CharField(max_length=50, default='Class 10')
    subject = models.CharField(max_length=100, default='Mathematics')
    chapter = models.CharField(max_length=200, blank=True, null=True)
    teacher_name = models.CharField(max_length=150, blank=True, null=True)
    
    meet_link = models.URLField(max_length=500, help_text='Google Meet / Zoom / Jitsi link')
    schedule_date = models.DateField()
    schedule_time = models.TimeField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Scheduled')
    started_at = models.DateTimeField(blank=True, null=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    actual_duration = models.CharField(max_length=50, blank=True, null=True)
    
    recorded_video_link = models.URLField(max_length=500, blank=True, null=True, help_text='YouTube / Drive / Vimeo recording link after class ends')
    recorded_video_file = models.FileField(
        upload_to=recorded_video_upload_path,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'webm', 'mkv', 'avi', 'mov'])],
        help_text='Direct MP4/WEBM video file upload'
    )
    
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-schedule_date', '-schedule_time']

    def save(self, *args, **kwargs):
        if not self.live_class_id:
            self.live_class_id = f"LC-{random.randint(100000, 999999)}"
        if not self.room_id:
            self.room_id = self.live_class_id
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.class_name} - {self.subject})"


# ============================================
# COURSES & BATCH LEARNING SYSTEM MODELS
# ============================================

class CourseBatch(models.Model):
    course_id = models.CharField(max_length=20, unique=True, blank=True)
    title = models.CharField(max_length=255)
    class_name = models.CharField(max_length=50, default='Class 10')
    stream = models.CharField(max_length=50, blank=True, null=True, default='N/A')
    subject = models.CharField(max_length=100, default='Mathematics')
    board = models.CharField(max_length=50, default='CBSE')
    language = models.CharField(max_length=50, default='Hinglish')
    tier = models.CharField(max_length=50, default='Normal')
    status = models.CharField(max_length=30, default='Active')
    batch_type = models.CharField(max_length=50, default='Live + Recorded')
    visibility = models.CharField(max_length=20, default='Public')
    launch_date = models.DateTimeField(blank=True, null=True)
    expiry_date = models.DateTimeField(blank=True, null=True)
    waitlist_enabled = models.BooleanField(default=False)
    rejection_reason = models.TextField(blank=True, null=True)
    class_timing = models.CharField(max_length=100, blank=True, null=True, default='4:00 PM - 6:00 PM')
    class_days = models.CharField(max_length=150, blank=True, null=True, default='Mon, Wed, Fri')
    branch = models.CharField(max_length=150, blank=True, null=True, default='Main Campus Room 101')
    current_enrollment_count = models.PositiveIntegerField(default=0)
    assigned_teachers = models.ManyToManyField('TeacherProfile', through='BatchTeacherAssignment', blank=True, related_name='assigned_batches')
    
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount_percent = models.PositiveIntegerField(default=0)
    is_free = models.BooleanField(default=False)

    price_normal = models.DecimalField(max_digits=10, decimal_places=2, default=1299.00)
    price_premium = models.DecimalField(max_digits=10, decimal_places=2, default=2499.00)
    price_ultra = models.DecimalField(max_digits=10, decimal_places=2, default=4999.00)

    discount_normal = models.PositiveIntegerField(default=20)
    discount_premium = models.PositiveIntegerField(default=30)
    discount_ultra = models.PositiveIntegerField(default=40)

    features_normal = models.TextField(blank=True, null=True)
    features_premium = models.TextField(blank=True, null=True)
    features_ultra = models.TextField(blank=True, null=True)
    
    banner_image = models.ImageField(upload_to='batch_banners/', blank=True, null=True)
    teacher_name = models.CharField(max_length=150, default='EduTrust Senior Faculty')
    
    description = models.TextField(blank=True, null=True)
    short_description = models.TextField(blank=True, null=True)
    academic_session = models.CharField(max_length=20, default='2026-27')
    course_type = models.CharField(max_length=50, default='Regular')
    course_status = models.CharField(max_length=20, default='Published')
    
    discount_type = models.CharField(max_length=20, default='Fixed Amount')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    final_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    installment_available = models.BooleanField(default=False)
    installment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    enrollment_start_date = models.DateField(blank=True, null=True)
    enrollment_end_date = models.DateField(blank=True, null=True)
    max_enrollment = models.PositiveIntegerField(default=100)
    free_trial_enabled = models.BooleanField(default=True)

    validity_months = models.PositiveIntegerField(default=12)
    start_date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.course_id:
            self.course_id = f"CRS-{random.randint(100000, 999999)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.class_name} - {self.subject})"


class BatchGroup(models.Model):
    batch_id = models.CharField(max_length=20, unique=True, blank=True)
    course = models.ForeignKey(CourseBatch, on_delete=models.CASCADE, related_name='batch_groups')
    batch_name = models.CharField(max_length=255)
    batch_code = models.CharField(max_length=50, blank=True, null=True)
    academic_session = models.CharField(max_length=20, default='2026-27')
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    batch_mode = models.CharField(max_length=50, default='Online')
    class_timing = models.CharField(max_length=100, blank=True, null=True)
    days = models.CharField(max_length=100, blank=True, null=True)
    max_students = models.PositiveIntegerField(default=50)
    branch_classroom = models.CharField(max_length=150, blank=True, null=True)
    lead_faculty = models.CharField(max_length=150, blank=True, null=True)
    batch_status = models.CharField(max_length=20, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.batch_id:
            self.batch_id = f"BTC-{random.randint(100000, 999999)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.batch_name} ({self.course.title})"


class CourseChapter(models.Model):
    course = models.ForeignKey(CourseBatch, on_delete=models.CASCADE, related_name='chapters', blank=True, null=True)
    subject = models.ForeignKey('CourseSubject', on_delete=models.SET_NULL, related_name='chapters', blank=True, null=True)
    chapter_title = models.CharField(max_length=255)
    sequence_number = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['sequence_number']

    def __str__(self):
        c_name = self.course.title if self.course else (self.subject.name if self.subject else 'General')
        return f"{c_name} - Ch {self.sequence_number}: {self.chapter_title}"


class CourseLecture(models.Model):
    chapter = models.ForeignKey(CourseChapter, on_delete=models.CASCADE, related_name='lectures')
    lecture_title = models.CharField(max_length=255)
    video_url = models.URLField(max_length=500)
    duration_minutes = models.PositiveIntegerField(default=45)
    is_free_demo = models.BooleanField(default=False)
    sequence_number = models.PositiveIntegerField(default=1)
    timestamps_json = models.TextField(blank=True, null=True, help_text='JSON array of timestamps [{time: "04:15", title: "Intro"}]')

    class Meta:
        ordering = ['sequence_number']

    def __str__(self):
        return f"{self.chapter.chapter_title} - Lec {self.sequence_number}: {self.lecture_title}"


class CourseMaterial(models.Model):
    chapter = models.ForeignKey(CourseChapter, on_delete=models.CASCADE, related_name='materials')
    title = models.CharField(max_length=255)
    material_type = models.CharField(max_length=50, choices=[('Class Notes', 'Class Notes'), ('Handwritten', 'Handwritten'), ('DPP', 'DPP')], default='Class Notes')
    file_url = models.URLField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.material_type})"


class CourseDoubt(models.Model):
    lecture = models.ForeignKey(CourseLecture, on_delete=models.CASCADE, related_name='doubts', blank=True, null=True)
    live_class = models.ForeignKey(LiveClass, on_delete=models.CASCADE, related_name='live_doubts', blank=True, null=True)
    student_name = models.CharField(max_length=150)
    question = models.TextField()
    timestamp = models.CharField(max_length=50, blank=True, null=True, help_text='Captured video timestamp e.g. 00:15:32')
    answer = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, default='Pending') # Pending, Answered, Resolved
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Doubt by {self.student_name} [{self.timestamp or '00:00'}]: {self.question[:30]}"


class LectureComment(models.Model):
    live_class = models.ForeignKey(LiveClass, on_delete=models.CASCADE, related_name='comments', blank=True, null=True)
    lecture = models.ForeignKey(CourseLecture, on_delete=models.CASCADE, related_name='comments', blank=True, null=True)
    student_name = models.CharField(max_length=150)
    user_role = models.CharField(max_length=50, default='Student')
    comment_text = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='replies', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.student_name}: {self.comment_text[:30]}"


class LectureProgress(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='lecture_progresses', blank=True, null=True)
    student_name = models.CharField(max_length=150)
    live_class = models.ForeignKey(LiveClass, on_delete=models.CASCADE, related_name='progresses', blank=True, null=True)
    lecture = models.ForeignKey(CourseLecture, on_delete=models.CASCADE, related_name='progresses', blank=True, null=True)
    last_position = models.FloatField(default=0.0)
    watched_duration = models.FloatField(default=0.0)
    completion_percentage = models.FloatField(default=0.0)
    completed = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.student_name} - {self.completion_percentage:.1f}%"


class CourseEnrollment(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='course_enrollments', blank=True, null=True)
    student_name = models.CharField(max_length=150)
    course = models.ForeignKey(CourseBatch, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=20, default='Success')
    progress_percent = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-enrolled_at']


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percent = models.PositiveIntegerField(default=10)
    max_uses = models.PositiveIntegerField(default=100)
    times_used = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} ({self.discount_percent}% OFF)"


class HomeworkAssignment(models.Model):
    course = models.ForeignKey(CourseBatch, on_delete=models.CASCADE, related_name='assignments', blank=True, null=True)
    chapter = models.ForeignKey(CourseChapter, on_delete=models.SET_NULL, related_name='dpps', blank=True, null=True)
    class_name = models.CharField(max_length=50, default='Class 10')
    subject = models.CharField(max_length=100, default='Mathematics')
    chapter_title = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    file_attachment = models.FileField(upload_to='assignments/', blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.class_name} - {self.subject}] {self.title}"


class HomeworkSubmission(models.Model):
    assignment = models.ForeignKey(HomeworkAssignment, on_delete=models.CASCADE, related_name='submissions')
    student_name = models.CharField(max_length=150)
    student_email = models.EmailField(blank=True, null=True)
    submission_file = models.FileField(upload_to='submissions/')
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Submitted') # Submitted, Evaluated

    def __str__(self):
        return f"{self.student_name} - {self.assignment.title}"


class NoticeBoard(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    action_link = models.URLField(max_length=500, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class DoubtQuery(models.Model):
    student_name = models.CharField(max_length=150, default='Student')
    batch_title = models.CharField(max_length=255, blank=True, null=True)
    query_text = models.TextField()
    image_query = models.ImageField(upload_to='doubts/', blank=True, null=True)
    ai_solution = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Doubt by {self.student_name}: {self.query_text[:30]}"


# ============================================
# PRODUCTION MODULE EXTENSION SCHEMAS
# ============================================

class ParentProfile(models.Model):
    parent_id = models.CharField(max_length=20, unique=True, blank=True)
    full_name = models.CharField(max_length=150)
    email = models.EmailField(blank=True, null=True)
    mobile = models.CharField(max_length=15, unique=True)
    occupation = models.CharField(max_length=100, blank=True, null=True)
    linked_student = models.ForeignKey(StudentProfile, on_delete=models.SET_NULL, blank=True, null=True, related_name='parents')
    account_status = models.CharField(max_length=20, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.parent_id:
            self.parent_id = f"PRN-{random.randint(100000, 999999)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.parent_id} - {self.full_name}"


class CourseSubject(models.Model):
    subject_id = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=100)
    subject_code = models.CharField(max_length=50, blank=True, null=True)
    faculty_name = models.CharField(max_length=150, blank=True, null=True, default='Faculty TBD')
    class_name = models.CharField(max_length=50, default='Class 10')
    course = models.ForeignKey(CourseBatch, on_delete=models.CASCADE, related_name='subjects', blank=True, null=True)
    sort_order = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, default='Published')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.subject_id:
            self.subject_id = f"SUB-{random.randint(100000, 999999)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.class_name})"


class TestSeries(models.Model):
    series_id = models.CharField(max_length=20, unique=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    validity_days = models.PositiveIntegerField(default=365)
    status = models.CharField(max_length=20, default='Published')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.series_id:
            self.series_id = f"TSR-{random.randint(100000, 999999)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class PreviousYearQuestion(models.Model):
    pyq_id = models.CharField(max_length=20, unique=True, blank=True)
    title = models.CharField(max_length=255)
    exam_name = models.CharField(max_length=100)
    year = models.CharField(max_length=10)
    subject = models.CharField(max_length=100)
    pdf_file = models.FileField(upload_to='pyq_pdfs/', blank=True, null=True)
    solution_file = models.FileField(upload_to='pyq_solutions/', blank=True, null=True)
    status = models.CharField(max_length=20, default='Published')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pyq_id:
            self.pyq_id = f"PYQ-{random.randint(100000, 999999)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.exam_name} ({self.year}) - {self.subject}"


class ELibraryBook(models.Model):
    book_id = models.CharField(max_length=20, unique=True, blank=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=150, default='Unknown Author')
    category = models.CharField(max_length=100, default='Reference')
    cover_image = models.ImageField(upload_to='library_covers/', blank=True, null=True)
    pdf_file = models.FileField(upload_to='library_pdfs/', blank=True, null=True)
    status = models.CharField(max_length=20, default='Published')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.book_id:
            self.book_id = f"LIB-{random.randint(100000, 999999)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ENewspaper(models.Model):
    paper_id = models.CharField(max_length=20, unique=True, blank=True)
    title = models.CharField(max_length=255)
    edition_date = models.DateField(default=timezone.now)
    pdf_file = models.FileField(upload_to='enewspapers/', blank=True, null=True)
    status = models.CharField(max_length=20, default='Published')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.paper_id:
            self.paper_id = f"NEWS-{random.randint(100000, 999999)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.edition_date})"


class Announcement(models.Model):
    announcement_id = models.CharField(max_length=20, unique=True, blank=True)
    title = models.CharField(max_length=255)
    message = models.TextField()
    target_audience = models.CharField(max_length=50, default='All Users')
    priority = models.CharField(max_length=20, default='Normal')
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.announcement_id:
            self.announcement_id = f"ANC-{random.randint(100000, 999999)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class DirectMessage(models.Model):
    sender_name = models.CharField(max_length=150)
    receiver_name = models.CharField(max_length=150)
    subject = models.CharField(max_length=255, blank=True, null=True)
    message_text = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"From {self.sender_name} to {self.receiver_name}"


class PaymentTransaction(models.Model):
    transaction_id = models.CharField(max_length=50, unique=True)
    invoice_number = models.CharField(max_length=50, blank=True, null=True)
    student_name = models.CharField(max_length=150)
    student_id_code = models.CharField(max_length=50, blank=True, null=True)
    student_email = models.EmailField(blank=True, null=True)
    course_title = models.CharField(max_length=255, default='Course Fee')
    batch_title = models.CharField(max_length=255, blank=True, null=True)
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    payment_method = models.CharField(max_length=50, default='UPI')
    gateway_name = models.CharField(max_length=50, default='Razorpay')
    gateway_txn_id = models.CharField(max_length=100, blank=True, null=True)
    
    status = models.CharField(max_length=30, default='Success') # Success, Pending, Failed, Cancelled, Refunded, Partially Refunded
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    refund_reason = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = f"INV-{random.randint(100000, 999999)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.transaction_id} ({self.invoice_number}) - ₹{self.amount} ({self.status})"



class WalletTransaction(models.Model):
    user_name = models.CharField(max_length=150)
    transaction_type = models.CharField(max_length=20, choices=[('Credit', 'Credit'), ('Debit', 'Debit')])
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    description = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class PlatformSettings(models.Model):
    site_name = models.CharField(max_length=150, default='EduTrust LMS')
    active_academic_session = models.CharField(max_length=20, default='2024-25')
    maintenance_mode = models.BooleanField(default=False)
    contact_email = models.EmailField(default='support@edutrust.com')
    contact_phone = models.CharField(max_length=20, default='+91 9876543210')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Settings ({self.active_academic_session})"


class AdminRole(models.Model):
    ROLE_TYPE_CHOICES = (
        ('System', 'System Role'),
        ('Custom', 'Custom Role'),
    )
    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    )

    role_name = models.CharField(max_length=100, unique=True)
    role_code = models.CharField(max_length=100, unique=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    role_type = models.CharField(max_length=20, choices=ROLE_TYPE_CHOICES, default='Custom')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    parent_role = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='child_roles')
    permissions_json = models.TextField(default='{}')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        verbose_name = "Admin Role"
        verbose_name_plural = "Admin Roles"
        ordering = ['role_name']

    def save(self, *args, **kwargs):
        if not self.role_code:
            import re
            self.role_code = re.sub(r'[^a-zA-Z0-9_]', '_', self.role_name.lower())
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.role_name} ({self.role_type})"


class UserRoleAssignment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='role_assignments')
    role = models.ForeignKey(AdminRole, on_delete=models.CASCADE, related_name='assigned_users')
    is_primary = models.BooleanField(default=True)
    assigned_by = models.CharField(max_length=150, default='Super Admin')
    start_date = models.DateField(default=timezone.now)
    expiry_date = models.DateField(blank=True, null=True)
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "User Role Assignment"
        verbose_name_plural = "User Role Assignments"
        unique_together = ['user', 'role']
        ordering = ['-assigned_at']

    def __str__(self):
        return f"{self.user.username} -> {self.role.role_name}"


class PermissionAuditLog(models.Model):
    admin_user = models.CharField(max_length=150, default='Super Admin')
    role_name = models.CharField(max_length=100)
    module_name = models.CharField(max_length=100)
    permission_key = models.CharField(max_length=100)
    old_value = models.CharField(max_length=100, blank=True, null=True)
    new_value = models.CharField(max_length=100, blank=True, null=True)
    action = models.CharField(max_length=50, default='UPDATE')
    ip_address = models.CharField(max_length=45, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Permission Audit Log"
        verbose_name_plural = "Permission Audit Logs"
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M')}] {self.admin_user} updated {self.role_name}.{self.module_name}"



class DatabaseBackup(models.Model):
    backup_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500, blank=True, null=True)
    file_size = models.CharField(max_length=50, default='1.2 MB')
    status = models.CharField(max_length=20, default='Completed')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.backup_name


class LocationSearchHistory(models.Model):
    SEARCH_TYPE_CHOICES = [
        ('top_teachers', 'Top Teachers'),
        ('latest_jobs', 'Latest Jobs'),
        ('hero_tutor_search', 'Hero Tutor Search'),
        ('current_location', 'Current Location'),
    ]

    user_name = models.CharField(max_length=150, blank=True, null=True)
    user_role = models.CharField(max_length=50, blank=True, null=True)
    session_id = models.CharField(max_length=128, blank=True, null=True)
    search_query = models.CharField(max_length=255, blank=True, null=True)
    selected_location = models.CharField(max_length=255)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    search_type = models.CharField(max_length=50, choices=SEARCH_TYPE_CHOICES, default='top_teachers')
    result_count = models.IntegerField(default=0)
    searched_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.CharField(max_length=500, blank=True, null=True)
    status = models.CharField(max_length=20, default='Success')

    class Meta:
        ordering = ['-searched_at']
        verbose_name_plural = 'Location Search History'

    def __str__(self):
        return f"{self.user_name or 'Guest'} - {self.selected_location} ({self.search_type})"


class ScheduledReport(models.Model):
    FREQUENCY_CHOICES = [
        ('Daily', 'Daily'),
        ('Weekly', 'Weekly'),
        ('Monthly', 'Monthly'),
    ]

    report_name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=100)  # e.g., students, revenue, courses, live_classes
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='Weekly')
    recipients = models.TextField(help_text="Comma-separated emails")
    file_format = models.CharField(max_length=20, default='CSV')  # CSV, Excel, PDF
    filters_json = models.TextField(blank=True, null=True, default='{}')
    status = models.CharField(max_length=20, default='Active')  # Active, Paused
    created_by = models.CharField(max_length=150, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_run = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.report_name} ({self.frequency} - {self.status})"


class GeneratedReport(models.Model):
    report_name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=100)
    generated_by = models.CharField(max_length=150, default='System')
    file_path = models.CharField(max_length=500, blank=True, null=True)
    file_size = models.CharField(max_length=50, default='0 KB')
    file_format = models.CharField(max_length=20, default='CSV')
    record_count = models.IntegerField(default=0)
    status = models.CharField(max_length=20, default='Completed')  # Completed, Processing, Failed
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.report_name} - {self.file_format} ({self.created_at.strftime('%Y-%m-%d')})"


class ExportHistoryLog(models.Model):
    report_name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=100)
    export_format = models.CharField(max_length=20, default='CSV')
    user_name = models.CharField(max_length=150, blank=True, null=True)
    record_count = models.IntegerField(default=0)
    file_size = models.CharField(max_length=50, default='0 KB')
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    exported_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-exported_at']

    def __str__(self):
        return f"{self.report_name} exported as {self.export_format} by {self.user_name or 'Admin'}"


class DPPSet(models.Model):
    dpp_id = models.CharField(max_length=20, unique=True, blank=True)
    title = models.CharField(max_length=255)
    class_name = models.CharField(max_length=50, default='Class 10')
    subject = models.CharField(max_length=100)
    chapter_title = models.CharField(max_length=255)
    subject_ref = models.ForeignKey(CourseSubject, on_delete=models.SET_NULL, null=True, blank=True, related_name='dpp_sets')
    chapter_ref = models.ForeignKey(CourseChapter, on_delete=models.SET_NULL, null=True, blank=True, related_name='dpp_sets')
    total_questions = models.PositiveIntegerField(default=20)
    total_marks = models.PositiveIntegerField(default=30)
    duration_mins = models.PositiveIntegerField(default=30)
    difficulty = models.CharField(max_length=20, default='Medium')  # Easy, Medium, Hard
    pdf_file = models.FileField(upload_to='dpp_pdfs/', blank=True, null=True)
    solution_pdf = models.FileField(upload_to='dpp_solutions/', blank=True, null=True)
    status = models.CharField(max_length=20, default='Published')  # Published, Draft
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.dpp_id:
            self.dpp_id = f"DPP-{random.randint(100000, 999999)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.class_name} - {self.subject} - {self.chapter_title}] {self.title}"


class StudentDPPAttempt(models.Model):
    student_name = models.CharField(max_length=150, default='Student')
    student_mobile = models.CharField(max_length=15, blank=True, null=True)
    dpp_set = models.ForeignKey(DPPSet, on_delete=models.CASCADE, related_name='student_attempts')
    status = models.CharField(max_length=20, default='Completed')  # Completed, Pending, In Progress
    score_obtained = models.PositiveIntegerField(default=18)
    total_marks = models.PositiveIntegerField(default=20)
    attempted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_name} - {self.dpp_set.title} ({self.status})"


class StudentParentEnquiry(models.Model):
    SOURCE_CHOICES = [
        ('STUDENT_REGISTRATION', 'Student Registration'),
        ('HIRE_A_TUTOR', 'Hire a Tutor'),
    ]
    STATUS_CHOICES = [
        ('NEW', 'New'),
        ('CONFIRMED', 'Confirmed'),
        ('REJECTED', 'Rejected'),
        ('CONTACTED', 'Contacted'),
        ('CLOSED', 'Closed'),
    ]

    full_name = models.CharField(max_length=150)
    parent_name = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    mobile = models.CharField(max_length=20)
    student_class = models.CharField(max_length=50, blank=True, null=True)
    board = models.CharField(max_length=50, blank=True, null=True)
    subject = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES, default='STUDENT_REGISTRATION')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='NEW')
    rejection_reason = models.TextField(blank=True, null=True)
    student_profile = models.ForeignKey(StudentProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='enquiries')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} ({self.get_source_display()}) - {self.status}"


class TeacherEnquiry(models.Model):
    SOURCE_CHOICES = [
        ('REGISTER_AS_TUTOR', 'Register as a Tutor'),
    ]
    STATUS_CHOICES = [
        ('NEW', 'New'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('SUSPENDED', 'Suspended'),
        ('CONTACTED', 'Contacted'),
        ('CLOSED', 'Closed'),
    ]

    full_name = models.CharField(max_length=150)
    email = models.EmailField(blank=True, null=True)
    mobile = models.CharField(max_length=20)
    qualification = models.CharField(max_length=150, blank=True, null=True)
    experience = models.CharField(max_length=50, blank=True, null=True)
    subjects = models.CharField(max_length=255, blank=True, null=True)
    preferred_classes = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    teaching_mode = models.CharField(max_length=100, blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES, default='REGISTER_AS_TUTOR')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='NEW')
    rejection_reason = models.TextField(blank=True, null=True)
    suspension_reason = models.TextField(blank=True, null=True)
    is_removed = models.BooleanField(default=False)
    removed_at = models.DateTimeField(blank=True, null=True)
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='enquiries')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} (Teacher Enquiry) - {self.status}"




class BatchTeacherAssignment(models.Model):
    batch = models.ForeignKey('CourseBatch', on_delete=models.CASCADE, related_name='teacher_assignments')
    teacher = models.ForeignKey('TeacherProfile', on_delete=models.CASCADE, related_name='batch_assignments')
    role_or_subject = models.CharField(max_length=100, blank=True, null=True, default='Primary Faculty')
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('batch', 'teacher')
        ordering = ['-assigned_at']

    def __str__(self):
        return f"{self.teacher.full_name} -> {self.batch.title}"


class BatchCoupon(models.Model):
    batch = models.ForeignKey('CourseBatch', on_delete=models.CASCADE, related_name='coupons')
    code = models.CharField(max_length=30, unique=True)
    discount_type = models.CharField(max_length=20, default='Percentage')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    min_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    usage_limit = models.PositiveIntegerField(default=100)
    used_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    expiry_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} ({self.batch.title})"


class BatchActivityLog(models.Model):
    batch = models.ForeignKey('CourseBatch', on_delete=models.CASCADE, related_name='activity_logs')
    user_name = models.CharField(max_length=150, default='Super Admin')
    user_role = models.CharField(max_length=50, default='Super Admin')
    action = models.CharField(max_length=100)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.action}] {self.batch.title} - {self.user_name}"


class TeacherJobApplication(models.Model):
    STATUS_CHOICES = [
        ('Applied', 'Applied'),
        ('Under Review', 'Under Review'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    ]

    application_id = models.CharField(max_length=50, unique=True)
    job_id = models.CharField(max_length=50)
    job_title = models.CharField(max_length=255)
    teacher = models.ForeignKey('TeacherProfile', on_delete=models.CASCADE, related_name='job_applications')
    
    applicant_name = models.CharField(max_length=150)
    email = models.EmailField()
    mobile = models.CharField(max_length=20)
    city = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    
    qualification = models.CharField(max_length=150, blank=True, null=True)
    experience = models.CharField(max_length=50, blank=True, null=True)
    subjects = models.CharField(max_length=255, blank=True, null=True)
    expected_fee = models.CharField(max_length=100, blank=True, null=True)
    teaching_mode = models.CharField(max_length=100, blank=True, null=True)
    
    source_page = models.CharField(max_length=50, default='Home Page')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Applied')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['job_id', 'teacher']

    def __str__(self):
        return f"{self.application_id} - {self.applicant_name} ({self.job_title})"




# ===========================
# Super Admin Security & OTP Models
# ===========================

class AdminOTP(models.Model):
    PURPOSE_CHOICES = (
        ('LOGIN', 'Super Admin Login'),
        ('PASSWORD_RESET', 'Password Reset'),
        ('USERNAME_CHANGE', 'Username Change'),
        ('EMAIL_CHANGE', 'Email Change'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_otps')
    otp_hash = models.CharField(max_length=128)
    purpose = models.CharField(max_length=30, choices=PURPOSE_CHOICES, default='LOGIN')
    new_email = models.EmailField(blank=True, null=True)
    new_username = models.CharField(max_length=150, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    attempt_count = models.IntegerField(default=0)
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"OTP for {self.user.username} ({self.purpose}) - Used: {self.is_used}"


class AdminSecurityLog(models.Model):
    EVENT_CHOICES = (
        ('LOGIN_SUCCESS', 'Login Successful'),
        ('LOGIN_FAILED', 'Login Failed'),
        ('LOGOUT', 'Logged Out'),
        ('OTP_SENT', 'OTP Sent'),
        ('OTP_VERIFIED', 'OTP Verified'),
        ('OTP_FAILED', 'OTP Verification Failed'),
        ('PASSWORD_CHANGED', 'Password Changed'),
        ('PASSWORD_RESET', 'Password Reset'),
        ('USERNAME_CHANGED', 'Username Changed'),
        ('EMAIL_CHANGED', 'Email Changed'),
        ('ACCOUNT_LOCKED', 'Account Locked'),
        ('ACCOUNT_UNLOCKED', 'Account Unlocked'),
        ('SESSION_EXPIRED', 'Session Expired'),
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='admin_security_logs')
    event = models.CharField(max_length=30, choices=EVENT_CHOICES)
    ip_address = models.CharField(max_length=45, blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, default='SUCCESS')
    description = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        username = self.user.username if self.user else 'System/Unknown'
        return f"[{self.event}] {username} at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"


# =========================================================
# SUPER ADMIN COMMUNICATION CENTER MODELS
# =========================================================

class CommunicationLog(models.Model):
    CHANNEL_CHOICES = (
        ('TEXT', 'Internal Text Message'),
        ('WHATSAPP', 'WhatsApp'),
        ('EMAIL', 'Email'),
        ('SMS', 'SMS'),
        ('NOTICE', 'Notice'),
        ('ANNOUNCEMENT', 'Announcement'),
        ('BROADCAST', 'Broadcast'),
        ('SUPPORT', 'Support'),
    )
    
    AUDIENCE_CHOICES = (
        ('INDIVIDUAL', 'Individual User'),
        ('MULTIPLE', 'Multiple Selected Users'),
        ('STUDENTS', 'All Students'),
        ('TEACHERS', 'All Teachers'),
        ('PARENTS', 'All Parents'),
        ('STAFF', 'All Staff'),
        ('CLASS', 'Specific Class'),
        ('COURSE', 'Specific Course'),
        ('GROUP', 'Group'),
        ('ALL', 'All Eligible Users'),
    )
    
    STATUS_CHOICES = (
        ('QUEUED', 'Queued'),
        ('SENT', 'Sent'),
        ('DELIVERED', 'Delivered'),
        ('READ', 'Read'),
        ('FAILED', 'Failed'),
    )
    
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_communications')
    recipient_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_communications')
    recipient_name = models.CharField(max_length=255, blank=True, default='')
    recipient_role = models.CharField(max_length=50, default='Student') # Student, Teacher, Parent, Staff, Admin
    recipient_contact = models.CharField(max_length=255, blank=True, default='') # Email or Phone
    
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default='TEXT')
    audience_type = models.CharField(max_length=20, choices=AUDIENCE_CHOICES, default='INDIVIDUAL')
    
    subject = models.CharField(max_length=255, blank=True, default='')
    message_text = models.TextField(blank=True, default='')
    attachment = models.FileField(upload_to='communication_attachments/', null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SENT')
    provider_message_id = models.CharField(max_length=255, blank=True, default='')
    
    is_starred = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    scheduled_for = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.channel}] {self.sender} -> {self.recipient_name or self.recipient_user} ({self.status})"


class CommunicationGroup(models.Model):
    group_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    group_avatar = models.ImageField(upload_to='group_avatars/', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    members = models.ManyToManyField(User, related_name='communication_groups', blank=True)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.group_name


class SupportTicket(models.Model):
    CATEGORY_CHOICES = (
        ('TECHNICAL', 'Technical Support'),
        ('LOGIN', 'Login / Account Issue'),
        ('PAYMENT', 'Payment / Fee Issue'),
        ('COURSE', 'Course / Study Material'),
        ('TEACHER', 'Teacher Inquiry'),
        ('STUDENT', 'Student Issue'),
        ('REFUND', 'Refund Request'),
        ('OTHER', 'Other Support'),
    )
    
    STATUS_CHOICES = (
        ('NEW', 'New'),
        ('OPEN', 'Open'),
        ('IN_PROGRESS', 'In Progress'),
        ('PENDING', 'Pending'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
    )
    
    PRIORITY_CHOICES = (
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    )
    
    ticket_id = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    user_name = models.CharField(max_length=255)
    user_role = models.CharField(max_length=50, default='Student')
    user_contact = models.CharField(max_length=255, blank=True, default='')
    
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='TECHNICAL')
    subject = models.CharField(max_length=255)
    description = models.TextField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_support_tickets')
    internal_note = models.TextField(blank=True, default='')
    is_starred = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.ticket_id}] {self.subject} ({self.status})"


class CommunicationTemplate(models.Model):
    title = models.CharField(max_length=255)
    channel = models.CharField(max_length=20, default='EMAIL')
    category = models.CharField(max_length=100, default='General')
    subject = models.CharField(max_length=255, blank=True, default='')
    template_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.channel})"


# ==========================================
# SUPER ADMIN LIVE CLASS MANAGEMENT MODELS
# ==========================================

class LiveClassAttendance(models.Model):
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Late', 'Late'),
        ('Left Early', 'Left Early'),
        ('Absent', 'Absent'),
    ]
    live_class = models.ForeignKey(LiveClass, on_delete=models.CASCADE, related_name='attendances')
    student = models.ForeignKey(StudentProfile, on_delete=models.SET_NULL, null=True, blank=True)
    student_name = models.CharField(max_length=200, default='Student')
    join_time = models.DateTimeField(auto_now_add=True)
    leave_time = models.DateTimeField(blank=True, null=True)
    duration_minutes = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Present')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-join_time']

    def __str__(self):
        return f"{self.student_name} - {self.live_class.title} ({self.status})"


class LiveClassQA(models.Model):
    live_class = models.ForeignKey(LiveClass, on_delete=models.CASCADE, related_name='qa_questions')
    asked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    question_text = models.TextField()
    answer_text = models.TextField(blank=True, null=True)
    is_answered = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return f"Q: {self.question_text[:50]} ({self.live_class.title})"


class LiveClassPoll(models.Model):
    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Published', 'Published'),
        ('Closed', 'Closed'),
    ]
    live_class = models.ForeignKey(LiveClass, on_delete=models.CASCADE, related_name='polls')
    question = models.CharField(max_length=300)
    options_json = models.JSONField(default=list, help_text='List of poll options')
    results_json = models.JSONField(default=dict, help_text='Option vote counts')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Published')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Poll: {self.question[:50]} ({self.status})"


class LiveClassChatMessage(models.Model):
    live_class = models.ForeignKey(LiveClass, on_delete=models.CASCADE, related_name='chat_messages')
    sender_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    sender_name = models.CharField(max_length=150, default='User')
    is_admin_teacher = models.BooleanField(default=False)
    message_text = models.TextField()
    is_pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender_name}: {self.message_text[:30]}"


# ==========================================
# SUPER ADMIN SYSTEM SETTINGS & AUDIT LOG MODELS
# ==========================================

class SystemSetting(models.Model):
    SETTING_TYPES = (
        ('string', 'String Text'),
        ('boolean', 'Boolean Switch'),
        ('integer', 'Integer Number'),
        ('decimal', 'Decimal Number'),
        ('json', 'JSON Structure'),
        ('url', 'URL Address'),
        ('email', 'Email Address'),
        ('file', 'File/Image Path'),
        ('color', 'Color Hex Code'),
    )

    category = models.CharField(max_length=64, db_index=True, help_text="Category e.g. general, branding, user_reg, academic, etc.")
    key = models.CharField(max_length=128, unique=True, db_index=True)
    value = models.TextField(blank=True, null=True)
    value_type = models.CharField(max_length=20, choices=SETTING_TYPES, default='string')
    description = models.CharField(max_length=255, blank=True, null=True)
    is_sensitive = models.BooleanField(default=False, help_text="Mask secret keys/passwords in API responses")
    is_public = models.BooleanField(default=False, help_text="Expose to public frontend context")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        verbose_name = "System Setting"
        verbose_name_plural = "System Settings"
        ordering = ['category', 'key']

    def __str__(self):
        return f"{self.category}.{self.key} = {self.value if not self.is_sensitive else '********'}"


class SettingsAuditLog(models.Model):
    ACTION_CHOICES = (
        ('CREATE', 'Created'),
        ('UPDATE', 'Updated'),
        ('RESET', 'Reset'),
        ('DELETE', 'Deleted'),
        ('ENABLE', 'Enabled'),
        ('DISABLE', 'Disabled'),
    )

    admin_user = models.CharField(max_length=150, default='Super Admin')
    setting_category = models.CharField(max_length=64, db_index=True)
    setting_key = models.CharField(max_length=128)
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, default='UPDATE')
    ip_address = models.CharField(max_length=45, blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Settings Audit Log"
        verbose_name_plural = "Settings Audit Logs"
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M')}] {self.admin_user} updated {self.setting_key}"

