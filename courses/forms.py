from datetime import timedelta

from django import forms
from django.utils import timezone

from glossary.models import Glossary

from .models import Course, CourseModeSchedule, Roster


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ("name", "description", "subject", "curriculum_context")
        widgets = {"curriculum_context": forms.Textarea(attrs={"rows": 10})}
        help_texts = {
            "curriculum_context": (
                "Optional. Paste the metadata-only curriculum-context.v1 JSON exported "
                "by your Curriculum Expert catalogue."
            )
        }


class RosterForm(forms.ModelForm):
    class Meta:
        model = Roster
        fields = ("name",)


class JoinCourseForm(forms.Form):
    join_code = forms.CharField(max_length=12, label="Course join code")

    def clean_join_code(self):
        return self.cleaned_data["join_code"].strip().upper()


class ExamModeForm(forms.Form):
    duration_minutes = forms.IntegerField(min_value=5, max_value=480, initial=60)

    def ends_at(self):
        return timezone.now() + timedelta(minutes=self.cleaned_data["duration_minutes"])


class CourseModeScheduleForm(forms.ModelForm):
    class Meta:
        model = CourseModeSchedule
        fields = ("starts_at", "ends_at")
        widgets = {
            "starts_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "ends_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }


class LinkGlossaryForm(forms.Form):
    glossary = forms.ModelChoiceField(queryset=Glossary.objects.none())

    def __init__(self, *args, teacher, course, **kwargs):
        super().__init__(*args, **kwargs)
        linked_ids = course.course_glossaries.values_list("glossary_id", flat=True)
        self.fields["glossary"].queryset = teacher.glossaries.exclude(pk__in=linked_ids).order_by(
            "title"
        )
