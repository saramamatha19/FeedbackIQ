"""
Closed-set theme taxonomy shared by classifier_prompt and summary_prompt.

Closed-set classification (vs. free-generation + fuzzy post-matching) is deliberate:
lexically dissimilar synonyms ("unable to login" / "can't sign in" / "login failed")
need semantic collapsing, which an LLM is good at — but the *output vocabulary* must
stay fixed so aggregation and dashboard charts all work deterministically against a
known enum instead of an ever-growing set of free-text labels. "Other" is a mandatory
escape hatch so the model is never forced to force-fit.
"""

CANONICAL_THEMES: list[str] = [
    "Login & Authentication",
    "Performance & Speed",
    "UI/UX & Design",
    "Pricing & Billing",
    "Customer Support",
    "Onboarding",
    "Mobile App",
    "Notifications",
    "Search & Discovery",
    "Data Export/Import",
    "Integrations & API",
    "Reliability & Bugs",
    "Security & Privacy",
    "Feature Request",
    "Documentation & Help",
    "Account Management",
    "Collaboration & Sharing",
    "Reporting & Analytics",
    "Accessibility",
    "Other",
]
