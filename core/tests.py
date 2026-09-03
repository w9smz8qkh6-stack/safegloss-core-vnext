from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from tests.helpers import SYNTHETIC_TEST_CREDENTIAL


class HomeTests(TestCase):
    def test_home_page_describes_public_core(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create multilingual glossaries")
        self.assertContains(response, "No provider account required")

    def test_health_endpoint(self):
        response = self.client.get(reverse("health"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_authenticated_workspace_exposes_landmarks_and_navigation(self):
        user = User.objects.create_user(
            email="teacher@example.test",
            password=SYNTHETIC_TEST_CREDENTIAL,
            role=User.Role.TEACHER,
        )
        self.client.force_login(user)

        response = self.client.get(reverse("dashboard"))

        self.assertContains(response, 'href="#main"', html=False)
        self.assertContains(response, 'aria-label="Application navigation"', html=False)
        self.assertContains(response, "Create your first course")
