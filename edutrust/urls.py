from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from TutionPlatform import views, admin_api_views
from bookings import views as booking_views

urlpatterns = [
    path('student/', views.study_material, name='student_dashboard'),
    path('student-dashboard/', views.study_material),
    path('admin-dashboard/', views.custom_admin, name='admin_dashboard'),
    path('admin-module/<str:module_name>/', views.admin_module_view, name='admin_module'),
    path('admin.html', views.custom_admin),

    # REAL ADMIN REST API ENDPOINTS
    path('api/admin/dashboard/stats/', admin_api_views.dashboard_stats_api, name='api_admin_dashboard_stats'),
    path('api/admin/students/', admin_api_views.students_api, name='api_admin_students'),
    path('api/admin/teachers/', admin_api_views.teachers_api, name='api_admin_teachers'),
    path('api/admin/courses/', admin_api_views.courses_api, name='api_admin_courses'),
    path('api/admin/courses/wizard/', admin_api_views.course_wizard_api, name='api_admin_course_wizard'),
    path('api/admin/batches/', admin_api_views.batches_api, name='api_admin_batches'),
    path('api/admin/batches/<int:batch_id>/', admin_api_views.batch_detail_api, name='api_admin_batch_detail'),
    path('api/admin/global-search/', admin_api_views.global_search_api, name='api_admin_global_search'),
    path('api/admin/notifications/', admin_api_views.notifications_api, name='api_admin_notifications'),
    path('api/admin/settings/', admin_api_views.settings_api, name='api_admin_settings'),
    path('api/admin/backup/', admin_api_views.backup_api, name='api_admin_backup'),
    path('api/admin/study-materials/', admin_api_views.study_materials_api, name='api_admin_study_materials'),
    path('api/admin/user-logs/', admin_api_views.user_logs_api, name='api_admin_user_logs'),
    path('api/admin/payments/', admin_api_views.payments_api, name='api_admin_payments'),
    path('api/admin/live-classes/', views.api_admin_live_classes, name='api_admin_live_classes'),
    path('api/admin/live-classes/create/', views.api_admin_live_class_create, name='api_admin_live_class_create'),
    path('api/admin/live-classes/<str:lc_id>/action/', views.api_admin_live_class_action, name='api_admin_live_class_action'),
    path('api/live-classes/upcoming/', views.api_live_classes_upcoming, name='api_live_classes_upcoming'),
    path('api/live-classes/active/', views.api_live_classes_active, name='api_live_classes_active'),
    path('api/live-classes/<str:lc_id>/start/', views.api_live_classes_start, name='api_live_classes_start'),
    path('api/live-classes/<str:lc_id>/end/', views.api_live_classes_end, name='api_live_classes_end'),
    path('api/live-classes/<str:lc_id>/join/', views.api_live_classes_join, name='api_live_classes_join'),
    path('api/live-classes/<str:lc_id>/', views.api_live_classes_detail, name='api_live_classes_detail'),
    path('notes/', views.notes_view, name='notes'),
    path('notes.html', views.notes_view),
    path('assignments/', views.assignments_view, name='assignments'),
    path('assignments.html', views.assignments_view),
    path('dpp/', views.dpp_view, name='dpp'),
    path('dpp.html', views.dpp_view),
    path('liveclasses.html', views.liveclasses, name='liveclasses_html'),
    path('liveclasses/', views.liveclasses, name='liveclasses_page'),
    path('recordedlectures.html', views.liveclasses, name='recorded_lectures_html'),
    path('recordedlectures/', views.liveclasses, name='recorded_lectures'),
    path('recorded-lectures/', views.liveclasses, name='recorded_lectures_slug'),
        # DEDICATED ADMIN ENQUIRY MODULE ROUTES
    path('admin/teacher-enquiries/', views.admin_teacher_enquiries, name='admin_teacher_enquiries'),
    path('admin/teacher-enquiries/<int:pk>/', views.admin_teacher_enquiry_detail, name='admin_teacher_enquiry_detail'),
    path('admin/student-parent-enquiries/', views.admin_student_parent_enquiries, name='admin_student_parent_enquiries'),
    path('admin/student-parent-enquiries/<int:pk>/', views.admin_student_parent_enquiry_detail, name='admin_student_parent_enquiry_detail'),
    path('admin/', views.custom_admin, name='custom_admin'),
    path('django-admin/', admin.site.urls),
    path('', include('TutionPlatform.urls')),

    path('find-tutor/', views.find_tutor, name='find_tutor'),
    path('latest-tuition-job/', views.latest_tuition_job, name='latest_tuition_job'),
    path('studymaterial/', views.study_material, name='study_material'),
    path('success/', views.success, name='success'),
    path('faqs/', views.faqs, name='faqs'),

    path('teacher-registration/', views.teacher_registration, name='teacher_registration'),
    path('student-registration/', views.student_registration, name='student_registration'),
    path('register.html', views.student_registration, name='register_html_root'),
    path('register/', views.student_registration, name='register_slug_root'),
    path('login/', views.login_view, name='login'),
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('hire/', views.hire, name='hire'),

    path('about/', views.about, name='about'),
    path('courses/', views.courses, name='courses'),
    path('contact/', views.contact, name='contact'),

    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),

    path('book-demo/', booking_views.book_demo_page, name='book_demo_page'),
    path('api/book-demo/', booking_views.book_demo_api, name='book_demo_api'),

    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)