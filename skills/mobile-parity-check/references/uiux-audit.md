# UI/UX audit matrix

Read when planning and executing the comparison. The main unit is a screen or user journey at an observable checkpoint, not a source file or API endpoint.

## Inventory the union

Map entry points, navigation destinations, sheets/dialogs, forms, settings, onboarding, account states, roles, feature gates, and important deep links from both apps. A feature visible on only one side stays in the inventory. Verify that an equivalent entry point is truly unavailable before calling it missing; a different menu location or feature flag may explain it.

Give screens and journeys stable IDs, with scenario/checkpoint variants such as `PROFILE-EDIT-001 / keyboard-open / before-save`. Record expected behavior and its source: reference app, user requirement, supplied design, documented convention, or unresolved. Do not guess that the newer commit is the better design.

For a full-app audit, every discovered screen needs a baseline comparison or an explicit blocked/not-run/excluded disposition. Use source inspection to guide exploration, then verify reachable screens in the running apps. Do not stop at the first few differences or compare only screens common to both apps.

## What to inspect

| Dimension | Observe and compare |
| --- | --- |
| Layout and hierarchy | Screen structure, grouping, alignment, spacing rhythm, content density, emphasis, primary/secondary action placement, sticky controls |
| Typography and copy | Font roles, relative sizes/weight, line height, wrapping, truncation, labels, errors, titles, units, terminology, capitalization |
| Brand and imagery | Color roles, contrast, icons and meaning, asset consistency, image crop/aspect ratio, placeholders, selected/disabled styling |
| Navigation and discovery | Entry points, screen titles, tab state, destination consistency, number of steps, back/up/dismiss, gestures, deep links |
| Interaction and feedback | Hit targets, enabled/disabled states, selection, pressed feedback, progress, completion/error feedback, cancel/retry, double taps |
| Forms and keyboards | Input types, focus order, next/done, keyboard occlusion, scroll-to-field, inline validation, required indicators, unsaved-change handling |
| State completeness | First use, loading, empty, populated, crowded, partial data, offline, timeout, failed save, retry, permission denial, expired session |
| Responsive behavior | Small displays, safe areas/insets, large text, dark/light mode, orientation where supported, content reaching the viewport edges |
| Accessibility | Accessible labels/roles/state, assistive focus order, text scaling, contrast, touch targets, readable error feedback, non-color cues |
| Motion and continuity | Transition/gesture behavior, layout jumps, flicker, interrupted loading, scroll/selection retention, return from background, reduced motion where applicable |

Use the app's actual risks to select additional variants. Small-screen clipping, large text, keyboard-open forms, and dark-mode states often deserve separate checkpoints. Cover supported languages/RTL when in scope, recording the language and locale. Do not imply every Cartesian combination was tested.

Compare user intent rather than identical tap coordinates. For a journey, record the steps/taps, availability of the next action, feedback, error recovery, and completion state. More steps can be a UX concern, but a platform convention or clearer flow may justify them. Explain the observed friction instead of equating fewer taps with better UX.

Check consistency inside each app as well as between them: the same action should use consistent naming and styling across screens. A defect shared by both platforms is still a quality issue and belongs in the report separately from cross-platform differences.

## Native platform differences

Do not require identical system fonts, navigation chrome, permission dialogs, keyboards, pickers, or standard gesture mechanics when native equivalents preserve the intent and quality. Assess whether controls are recognizable, reachable, labeled, and appropriate to the platform. A missing action, lost state, misleading label, or hidden primary button is not excused by native styling.

Mark a difference `intentional` only with a documented/accepted rationale or a clearly identified native convention and equivalent observed outcome. Record that basis. If the design intent is unclear, keep it as an unresolved difference or optional recommendation rather than silently dismissing it or demanding a redesign.

## Visual evidence

Capture the same fixture, screen, semantic checkpoint, scroll position, and environment variant. Record logical dimensions and pixel scale. Compare equivalent content regions; pixel dimensions alone are not comparable points/dp. Preserve raw captures and explain any alignment, crop, or OS-chrome mask. Never stretch different aspect ratios to force a match or mask the product defect itself.

For each compared screen, create a linked side-by-side evidence pair, including matched screens in the coverage gallery when practical. For findings, identify the exact affected region with coordinates or a separately labeled annotation/zoom if available. Keep raw screenshots beside derived views. Do not use generative image editing to make evidence or annotations.

Use recordings and timestamps for motion, transitions, gestures, focus jumps, and perceived delays. Call a timing difference measured only if timing was actually captured under comparable conditions. Simulator performance does not establish real-device performance.

Record the method used for accessibility: hierarchy inspection, test assertions, visual contrast assessment, or actual assistive navigation. Labels observed in a UI tree are not proof that VoiceOver/TalkBack interaction was tested. Mark unsupported checks unverified.

## Classify without overstating

- **Parity defect:** a verified difference causes missing/misleading content, broken flow, inconsistent product behavior, or a failure to meet the designated design requirement.
- **Intentional variation:** a supported native/design choice with comparable task outcome; document the rationale.
- **Shared UX issue:** both apps exhibit the same clipping, unclear feedback, inaccessible control, or other demonstrated problem.
- **Improvement suggestion:** a design recommendation without evidence that either app violates the reference/requirement; keep it separate and state the benefit.
- **Harness/environment problem:** unequal fixtures, stale build, unsupported input, missing automation, or unavailable integration prevents a fair comparison.

Prioritize by user impact: an inaccessible or obscured primary action matters more than a harmless one-pixel alignment difference. Describe the observation concretely and connect it to the user's task. Keep broader business logic, security, backend, and performance audits outside scope unless explicitly requested or directly needed to explain the UI/UX evidence.
