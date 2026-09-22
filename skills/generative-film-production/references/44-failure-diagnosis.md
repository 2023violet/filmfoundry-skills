# Visual and Generation Failure Diagnosis

When a result is weak, diagnose the narrowest failing layer before rewriting the
Prompt or changing the model.

| Observable symptom | First check | Typical repair |
|---|---|---|
| Person looks pasted into the scene | common light, scale, occlusion, contact, focus | repair keyframe integration or location reference |
| Identity or wardrobe drifts | identity/state reference responsibility | use the correct state authority or split the shot |
| Architecture or spatial direction changes | location geometry and camera orientation | add a spatial map or rebuild the composition |
| Camera and action fight each other | dominant action and physical camera path | simplify to one action and one camera logic |
| Beautiful image cannot be edited | Shot Spec and observable end state | compile for editability, not aesthetics alone |
| Grid/contact-sheet views disagree | reference role and geometry assumptions | treat exploration views as non-authoritative |
| Palette or texture drifts | Style Profile version and style references | lock style variables without changing story facts |
| Motion is unstable or overactive | motion density and controllability budget | reduce stages, speed, and simultaneous changes |
| Result is close but not approved | Gate and Select status | keep `RELATIVE_BEST`/`HUMAN_REVIEW`; do not promote silently |

Diagnosis order:

1. Check the Shot Spec and required visible facts.
2. Check reference roles and profile versions.
3. Check subject–scene integration and state alignment.
4. Check camera/action/timing load.
5. Only then change one Prompt variable or adapter setting tied to evidence.

Do not use aesthetic preference to conceal a structural failure. Record the failure,
the suspected cause, and the single change made for the next attempt.
