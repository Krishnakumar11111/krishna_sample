import json
from django.test import TestCase, Client
from django.urls import reverse
from bookings.models import FreeTrialBooking
from TutionPlatform.models import ActivityLog, AdminNotification, TeacherProfile


class DemoBookingTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_book_demo_page_routing(self):
        response = self.client.get('/book-demo/')
        self.assertEqual(response.status_code, 200)

    def test_book_demo_api_valid_submission(self):
        payload = {
            "student": {
                "name": "Rohan Gupta",
                "mobile": "9876543210",
                "email": "rohan@example.com",
                "class": "Class 10",
                "gender": "Male"
            },
            "tuition": {
                "subject": "Mathematics",
                "mode": "Home Tuition",
                "date": "2026-08-20",
                "timeSlot": "05:00 PM - 06:00 PM",
                "address": {
                    "city": "Lucknow",
                    "state": "Uttar Pradesh",
                    "complete": "Hazratganj, Lucknow"
                }
            }
        }

        response = self.client.post('/api/book-demo/', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('status'), 'success')
        self.assertTrue(data.get('booking_id').startswith('DEMO-'))

        # Verify DB records created atomically
        booking = FreeTrialBooking.objects.get(booking_id=data.get('booking_id'))
        self.assertEqual(booking.student_name, "Rohan Gupta")
        self.assertEqual(booking.student_mobile, "9876543210")

        # Verify Activity Log and Admin Notification
        self.assertTrue(ActivityLog.objects.filter(activity_type='Demo Class Booked').exists())
        self.assertTrue(AdminNotification.objects.filter(category='demo_booking').exists())

    def test_book_demo_api_validation_errors(self):
        invalid_payload = {
            "student": {
                "name": "",
                "mobile": "123",
                "email": "invalid-email",
                "class": ""
            },
            "tuition": {
                "subject": ""
            }
        }

        response = self.client.post('/api/book-demo/', data=json.dumps(invalid_payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data.get('status'), 'error')
        self.assertIn('errors', data)

    def test_booking_id_collision_prevention(self):
        booking1 = FreeTrialBooking.objects.create(
            student_name="Student 1",
            student_mobile="9876543211",
            student_email="student1@example.com",
            student_class="Class 9",
            subject="Science",
            tuition_mode="Online"
        )
        self.assertTrue(booking1.booking_id.startswith('DEMO-'))

        booking2 = FreeTrialBooking.objects.create(
            student_name="Student 2",
            student_mobile="9876543212",
            student_email="student2@example.com",
            student_class="Class 11",
            subject="Physics",
            tuition_mode="Home Tuition"
        )
        self.assertNotEqual(booking1.booking_id, booking2.booking_id)

    def test_teacher_assignment(self):
        teacher = TeacherProfile.objects.create(
            full_name="Dr. Anil Sharma",
            email="anil@example.com",
            mobile="9812345678",
            qualification="Ph.D Physics",
            experience="10 Years",
            city="Lucknow"
        )

        booking = FreeTrialBooking.objects.create(
            student_name="Student 3",
            student_mobile="9876543213",
            student_email="student3@example.com",
            student_class="Class 12",
            subject="Physics",
            tuition_mode="Home Tuition",
            assigned_teacher=teacher,
            booking_status="Teacher Assigned"
        )

        self.assertEqual(booking.assigned_teacher, teacher)
        self.assertEqual(booking.assigned_teacher.teacher_id, teacher.teacher_id)
        self.assertEqual(booking.booking_status, "Teacher Assigned")
