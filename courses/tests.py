import json
from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from tests.helpers import SYNTHETIC_TEST_CREDENTIAL

from .models import Course, CourseModeSchedule, Enrollment


class CourseAccessTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            email="teacher@example.test",
            password=SYNTHETIC_TEST_CREDENTIAL,
            role=User.Role.TEACHER,
        )
        self.student = User.objects.create_user(
            email="student@example.test",
            password=SYNTHETIC_TEST_CREDENTIAL,
            role=User.Role.STUDENT,
        )
        self.other_student = User.objects.create_user(
            email="other@example.test",
            password=SYNTHETIC_TEST_CREDENTIAL,
            role=User.Role.STUDENT,
        )
        self.course = Course.objects.create(teacher=self.teacher, name="Biology")

    def test_student_can_join_with_code(self):
        self.client.force_login(self.student)
        response = self.client.post(
            reverse("courses:join"), {"join_code": self.course.join_code.lower()}
        )
        self.assertRedirects(response, reverse("courses:detail", args=[self.course.pk]))
        self.assertTrue(
            Enrollment.objects.filter(course=self.course, student=self.student).exists()
        )

    def test_unenrolled_student_cannot_view_course(self):
        self.client.force_login(self.other_student)
        response = self.client.get(reverse("courses:detail", args=[self.course.pk]))
        self.assertEqual(response.status_code, 403)

    def test_student_cannot_create_course(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("courses:create"))
        self.assertEqual(response.status_code, 403)

    def test_teacher_can_attach_a_curriculum_context_without_copying_taxonomy(self):
        self.client.force_login(self.teacher)
        context = {
            "schema": "curriculum-context.v1",
            "context_id": "course-version:14",
            "catalogue_release": "course-version:14:2026-09-04T00:00:00Z",
            "selection": {
                "primary_path": ["authority", "program", "biology", "2026"],
                "requirement_ids": ["requirement:12"],
            },
            "display": {
                "authority": "Example Authority",
                "program": "Science",
                "grade_band": "Years 10–11",
                "subject_area": "Science and technology",
                "course": "Biology",
                "course_version": "2026",
                "requirement_labels": ["Cells"],
            },
        }
        response = self.client.post(
            reverse("courses:create"),
            {
                "name": "Aligned Biology",
                "description": "",
                "subject": "",
                "curriculum_context": json.dumps(context),
            },
        )
        course = Course.objects.get(name="Aligned Biology")
        self.assertRedirects(response, reverse("courses:detail", args=[course.pk]))
        self.assertEqual(
            course.curriculum_context["selection"]["requirement_ids"], ["requirement:12"]
        )

    def test_course_rejects_an_unversioned_curriculum_payload(self):
        course = Course(
            teacher=self.teacher, name="Biology", curriculum_context={"schema": "other"}
        )
        with self.assertRaises(Exception):
            course.full_clean()


class ExamModeTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            email="teacher@example.test",
            password=SYNTHETIC_TEST_CREDENTIAL,
            role=User.Role.TEACHER,
        )
        self.course = Course.objects.create(teacher=self.teacher, name="Chemistry")

    def test_manual_exam_mode_expires(self):
        self.course.mode = Course.Mode.EXAM
        self.course.exam_mode_until = timezone.now() - timedelta(minutes=1)
        self.course.save()
        self.assertFalse(self.course.is_exam_mode)

    def test_active_schedule_enables_exam_mode(self):
        CourseModeSchedule.objects.create(
            course=self.course,
            starts_at=timezone.now() - timedelta(minutes=1),
            ends_at=timezone.now() + timedelta(minutes=30),
            created_by=self.teacher,
        )
        self.assertTrue(self.course.is_exam_mode)
