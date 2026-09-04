import secrets

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


def generate_join_code():
    return secrets.token_urlsafe(6).replace("-", "").replace("_", "")[:8].upper()


class Course(models.Model):
    class Mode(models.TextChoices):
        STUDY = "study", "Study Mode"
        EXAM = "exam", "Exam Mode"

    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="taught_courses",
    )
    name = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    subject = models.ForeignKey(
        "core.Subject",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="courses",
    )
    curriculum_context = models.JSONField(
        default=dict,
        blank=True,
        help_text=(
            "Optional curriculum-context.v1 selection exported by Curriculum Expert. "
            "SafeGloss stores the selection, not a copy of the provider taxonomy."
        ),
    )
    mode = models.CharField(max_length=12, choices=Mode.choices, default=Mode.STUDY)
    exam_mode_until = models.DateTimeField(null=True, blank=True)
    join_code = models.CharField(max_length=12, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)

    def save(self, *args, **kwargs):
        if not self.join_code:
            for _ in range(10):
                candidate = generate_join_code()
                if not Course.objects.filter(join_code=candidate).exists():
                    self.join_code = candidate
                    break
            else:
                raise RuntimeError("Unable to allocate a unique course join code.")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        context = self.curriculum_context
        if not context:
            return
        if not isinstance(context, dict) or context.get("schema") != "curriculum-context.v1":
            raise ValidationError(
                {
                    "curriculum_context": (
                        "Paste a curriculum-context.v1 package from Curriculum Expert."
                    )
                }
            )
        selection = context.get("selection")
        if not isinstance(selection, dict) or not all(
            isinstance(selection.get(key), list) for key in ("primary_path", "requirement_ids")
        ):
            raise ValidationError(
                {
                    "curriculum_context": (
                        "The selection must include primary_path and requirement_ids lists."
                    )
                }
            )
        display = context.get("display")
        if not isinstance(display, dict):
            raise ValidationError(
                {"curriculum_context": "The context must include display metadata."}
            )

    @property
    def curriculum_context_label(self):
        display = (self.curriculum_context or {}).get("display", {})
        return display.get("course", "Curriculum context")

    @property
    def is_exam_mode(self):
        now = timezone.now()
        manually_active = self.mode == self.Mode.EXAM and (
            self.exam_mode_until is None or self.exam_mode_until > now
        )
        scheduled = self.mode_schedules.filter(starts_at__lte=now, ends_at__gt=now).exists()
        return manually_active or scheduled

    def set_study_mode(self):
        self.mode = self.Mode.STUDY
        self.exam_mode_until = None
        self.save(update_fields=["mode", "exam_mode_until", "updated_at"])


class CourseModeSchedule(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="mode_schedules")
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        ordering = ("starts_at",)

    def clean(self):
        if self.ends_at <= self.starts_at:
            raise ValidationError({"ends_at": "The end time must be after the start time."})

    def __str__(self):
        return f"{self.course}: {self.starts_at:%Y-%m-%d %H:%M}"


class Roster(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="rosters")
    name = models.CharField(max_length=120)

    class Meta:
        ordering = ("name",)
        constraints = [
            models.UniqueConstraint(fields=("course", "name"), name="unique_roster_name")
        ]

    def __str__(self):
        return f"{self.course}: {self.name}"


class Enrollment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    roster = models.ForeignKey(
        Roster,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="enrollments",
    )
    native_language = models.ForeignKey(
        "core.Language",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="enrollments",
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("course", "student"), name="unique_course_student")
        ]

    def clean(self):
        if self.roster_id and self.roster.course_id != self.course_id:
            raise ValidationError({"roster": "The roster must belong to this course."})

    def __str__(self):
        return f"{self.student} in {self.course}"


class CourseGlossary(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="course_glossaries")
    glossary = models.ForeignKey(
        "glossary.Glossary",
        on_delete=models.CASCADE,
        related_name="course_links",
    )
    linked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("course", "glossary"), name="unique_course_glossary")
        ]

    def __str__(self):
        return f"{self.course}: {self.glossary}"
