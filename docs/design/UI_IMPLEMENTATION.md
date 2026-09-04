# Core application UI implementation

Status: current implementation guidance for the server-rendered Core application.

The Core interface is a calm, precise, information-rich workspace for teachers
and learners. It implements the shared [interface standard](INTERFACE_STANDARD.md)
with a small, local semantic CSS layer so a self-hosted installation has no
front-end provider dependency.

## Design contract

- Each page or work region has one visually primary action; secondary actions
  use an outlined treatment and destructive actions are visibly separated.
- Authenticated wide layouts have a persistent 240px navigation rail,
  intermediate layouts use an icon rail, and narrow layouts retain the same
  destinations in a horizontal navigation strip.
- Forms retain Django server-side validation and render visible labels, inline
  errors, and a non-field error summary when applicable.
- Study and Exam Mode pair text with a semantic status indicator. Colour alone
  never carries state.

## Tokens and self-hosting

The CSS custom properties in `config/static/css/app.css` are the Core token
source: blue action scale, neutral page and surface layers, semantic status
colours, focus ring, radius, and type fallback. The stylesheet also responds to
the system colour preference without changing server-side content or behavior.

No identity, analytics, AI, font, icon, or front-end provider is required to
render this interface. Future Bootstrap or HTMX adoption must preserve the
semantic tokens, server-side validation, keyboard behavior, and responsive
contracts recorded here.

## Review scope

Review home, authentication, dashboard, course, glossary, import, and learner
course-glossary views at narrow, intermediate, and wide widths. Check keyboard
focus, form errors, long labels, empty collections, Study/Exam state, and print
output. WCAG 2.2 AA remains a design target; this document does not make a
product-wide conformance claim.
