# SafeGloss Core authorization model

Authorization is enforced in Django views and queries. Template visibility is
only presentation and is never the security boundary.

## Roles

- Anonymous visitors can use the landing, login, signup, and health routes.
- Authenticated students can join courses and access courses for which they
  have an active enrollment.
- A user is treated as a teacher when their role is `teacher` or their Django
  `is_staff` flag is true.
- Django superusers and staff can access the admin according to Django admin
  permissions. Staff status does not automatically bypass every object-owner
  query in ordinary teacher mutation views.

These rules describe the current application and `accounts.User`. The dormant
`safegloss_core_identity.User` package has no product-role, organization,
membership, entitlement, provider, or legacy-privilege fields and is not
selected by the default settings. Its manager hashes credentials, requires an
email identifier, and refuses malformed superuser flags; it does not import or
infer authority. Activating a successor authorization model is a later
reviewed composition and data-migration change, not part of this identity root.

## Capability matrix

| Capability | Anonymous | Student | Teacher | Staff/admin |
|---|---:|---:|---:|---:|
| Landing, login, signup, health | yes | yes | yes | yes |
| Personal dashboard | no | yes | yes | yes |
| Join course by code | no | yes | yes, except own course | yes, except own course |
| View course | no | active enrollment | owned course | staff read path or enrollment |
| Create course or glossary | no | no | yes | yes |
| Mutate course | no | no | owned course | only when explicit owner query matches |
| Mutate glossary terms/translations | no | no | owned glossary | only when explicit owner query matches |
| View linked glossary | no | active enrollment and link | owned/accessible course | staff read path where implemented |
| View public glossary | no | yes | yes | yes |
| Django administration | no | no | only if separately granted staff permission | subject to Django admin permissions |

## Enforcement points

- `accounts.decorators.teacher_required` requires authentication and teacher
  status.
- `courses.views.course_for_user` permits the course owner, staff, or a student
  with active enrollment.
- Course mutation views query the requested course with `teacher=request.user`.
- `glossary.views.accessible_glossaries` combines public, creator-owned,
  teacher-course-linked, and active-student-enrollment visibility.
- Glossary mutation views query through `creator=request.user`.
- Course glossary rendering verifies both course access and the exact
  course/glossary link.
- Exam Mode applies additional course and term restrictions to students.
- All mutating browser routes use Django CSRF protection; destructive actions
  shown in this product use POST.

The generated [route inventory](../generated/routes.md) is the current route
surface. Any new view must define its authentication, role, object, method,
and Exam Mode behavior and add tests for allowed and rejected access.

## Invariants for changes

1. Authorization remains server-side and object-scoped.
2. A public glossary flag never grants mutation rights.
3. Enrollment access requires `is_active=True`.
4. Linking a glossary does not transfer glossary ownership.
5. Staff behavior must be explicit; do not assume the admin role is a universal
   bypass in product views.
6. Exam Mode restrictions must be applied before content is rendered or
   exported, not hidden only with CSS or JavaScript.
