# Eval Report — classifier_prompt v1.0

Generated: 2026-07-20T18:38:41.409431+00:00
Dataset size: 31 items

## Field Accuracy

| Field | Accuracy |
|---|---|
| category | 83.9% |
| sentiment | 96.8% |
| theme | 83.9% |
| urgency | 71.0% |
| emotion | 87.1% |

**Overall exact-match accuracy (all 5 fields correct): 58.1%**

## Confidence Calibration

- Average confidence: 75.2
- Average confidence when fully correct: 75.2
- Average confidence when any field wrong: 75.2

(A well-calibrated model shows a meaningfully lower average confidence on the incorrect group — that gap is what makes the `needs_human_review` flag useful rather than decorative.)

## Performance

- Average processing time per item: 1090.1 ms
- Fallback rate (both attempts failed validation): 0.0%

## Per-Item Breakdown

| ID | Type | Category | Sentiment | Theme | Urgency | Emotion | Confidence |
|---|---|---|---|---|---|---|---|
| typo_1 | typo | ✅ | ✅ | ✅ | ❌ (got High, want Medium) | ✅ | 80 |
| typo_2 | typo | ❌ (got Bug, want Complaint) | ✅ | ✅ | ❌ (got High, want Medium) | ✅ | 80 |
| typo_3 | typo | ✅ | ✅ | ✅ | ❌ (got High, want Medium) | ✅ | 83 |
| emoji_1 | emoji | ✅ | ✅ | ✅ | ✅ | ✅ | 90 |
| emoji_2 | emoji | ✅ | ✅ | ✅ | ✅ | ✅ | 90 |
| emoji_3 | emoji | ✅ | ✅ | ❌ (got Reliability & Bugs, want Other) | ❌ (got High, want Medium) | ❌ (got Disappointment, want Frustration) | 75 |
| sarcasm_1 | sarcasm | ✅ | ✅ | ✅ | ✅ | ✅ | 78 |
| sarcasm_2 | sarcasm | ✅ | ✅ | ✅ | ✅ | ✅ | 80 |
| sarcasm_3 | sarcasm | ✅ | ✅ | ✅ | ✅ | ✅ | 80 |
| mixed_lang_1 | mixed_language | ✅ | ✅ | ✅ | ✅ | ✅ | 85 |
| mixed_lang_2 | mixed_language | ✅ | ✅ | ✅ | ✅ | ✅ | 80 |
| short_1 | one_word | ✅ | ✅ | ✅ | ✅ | ✅ | 35 |
| short_2 | one_word | ✅ | ✅ | ✅ | ✅ | ✅ | 20 |
| long_1 | long_rambling | ❌ (got Complaint, want Bug) | ✅ | ✅ | ❌ (got High, want Medium) | ✅ | 80 |
| long_2 | long_rambling | ✅ | ✅ | ❌ (got Reliability & Bugs, want Data Export/Import) | ✅ | ✅ | 85 |
| multi_1 | multi_issue | ✅ | ✅ | ✅ | ✅ | ✅ | 65 |
| multi_2 | multi_issue | ❌ (got Feature Request, want Bug) | ✅ | ❌ (got UI/UX & Design, want Performance & Speed) | ✅ | ✅ | 70 |
| multi_3 | multi_issue | ✅ | ✅ | ✅ | ❌ (got High, want Medium) | ❌ (got Satisfaction, want Frustration) | 65 |
| ambiguous_1 | ambiguous | ✅ | ✅ | ✅ | ✅ | ✅ | 25 |
| ambiguous_2 | ambiguous | ❌ (got Question, want Bug) | ❌ (got Neutral, want Negative) | ❌ (got Data Export/Import, want Reporting & Analytics) | ✅ | ✅ | 60 |
| ambiguous_3 | ambiguous | ❌ (got Other, want Complaint) | ✅ | ❌ (got Other, want Reporting & Analytics) | ❌ (got Medium, want Low) | ✅ | 30 |
| dup_login_1 | duplicate_cluster | ✅ | ✅ | ✅ | ✅ | ✅ | 90 |
| dup_login_2 | duplicate_cluster | ✅ | ✅ | ✅ | ✅ | ✅ | 90 |
| dup_login_3 | duplicate_cluster | ✅ | ✅ | ✅ | ✅ | ❌ (got Frustration, want Anger) | 90 |
| dup_crash_1 | duplicate_cluster | ✅ | ✅ | ✅ | ❌ (got High, want Critical) | ✅ | 90 |
| dup_crash_2 | duplicate_cluster | ✅ | ✅ | ✅ | ❌ (got High, want Critical) | ❌ (got Frustration, want Anger) | 90 |
| dup_crash_3 | duplicate_cluster | ✅ | ✅ | ✅ | ✅ | ✅ | 90 |
| contra_ui_1 | contradiction_pair | ✅ | ✅ | ✅ | ✅ | ✅ | 90 |
| contra_ui_2 | contradiction_pair | ✅ | ✅ | ✅ | ✅ | ✅ | 85 |
| contra_export_1 | contradiction_pair | ✅ | ✅ | ✅ | ✅ | ✅ | 90 |
| contra_export_2 | contradiction_pair | ✅ | ✅ | ✅ | ✅ | ✅ | 90 |