# Eval Report — classifier_prompt v1.1

Generated: 2026-07-20T18:40:34.867861+00:00
Dataset size: 31 items

## Field Accuracy

| Field | Accuracy |
|---|---|
| category | 87.1% |
| sentiment | 96.8% |
| theme | 80.6% |
| urgency | 80.6% |
| emotion | 90.3% |

**Overall exact-match accuracy (all 5 fields correct): 54.8%**

## Confidence Calibration

- Average confidence: 74.6
- Average confidence when fully correct: 74.7
- Average confidence when any field wrong: 74.4

(A well-calibrated model shows a meaningfully lower average confidence on the incorrect group — that gap is what makes the `needs_human_review` flag useful rather than decorative.)

## Performance

- Average processing time per item: 1194.5 ms
- Fallback rate (both attempts failed validation): 0.0%

## Per-Item Breakdown

| ID | Type | Category | Sentiment | Theme | Urgency | Emotion | Confidence |
|---|---|---|---|---|---|---|---|
| typo_1 | typo | ✅ | ✅ | ✅ | ❌ (got High, want Medium) | ✅ | 80 |
| typo_2 | typo | ✅ | ✅ | ✅ | ❌ (got High, want Medium) | ✅ | 85 |
| typo_3 | typo | ✅ | ✅ | ✅ | ❌ (got High, want Medium) | ✅ | 82 |
| emoji_1 | emoji | ✅ | ✅ | ✅ | ✅ | ✅ | 70 |
| emoji_2 | emoji | ✅ | ✅ | ✅ | ✅ | ✅ | 85 |
| emoji_3 | emoji | ✅ | ✅ | ❌ (got Reliability & Bugs, want Other) | ✅ | ✅ | 75 |
| sarcasm_1 | sarcasm | ✅ | ✅ | ✅ | ✅ | ✅ | 75 |
| sarcasm_2 | sarcasm | ✅ | ✅ | ✅ | ❌ (got High, want Medium) | ✅ | 80 |
| sarcasm_3 | sarcasm | ✅ | ✅ | ✅ | ✅ | ✅ | 85 |
| mixed_lang_1 | mixed_language | ✅ | ✅ | ✅ | ✅ | ✅ | 90 |
| mixed_lang_2 | mixed_language | ✅ | ✅ | ✅ | ✅ | ✅ | 85 |
| short_1 | one_word | ✅ | ✅ | ✅ | ✅ | ✅ | 35 |
| short_2 | one_word | ✅ | ✅ | ✅ | ✅ | ✅ | 30 |
| long_1 | long_rambling | ❌ (got Feature Request, want Bug) | ✅ | ❌ (got UI/UX & Design, want Search & Discovery) | ✅ | ✅ | 80 |
| long_2 | long_rambling | ✅ | ✅ | ❌ (got Reliability & Bugs, want Data Export/Import) | ✅ | ✅ | 85 |
| multi_1 | multi_issue | ✅ | ✅ | ✅ | ✅ | ✅ | 65 |
| multi_2 | multi_issue | ❌ (got Feature Request, want Bug) | ✅ | ❌ (got UI/UX & Design, want Performance & Speed) | ✅ | ✅ | 55 |
| multi_3 | multi_issue | ✅ | ✅ | ✅ | ✅ | ❌ (got Neutral, want Frustration) | 60 |
| ambiguous_1 | ambiguous | ✅ | ✅ | ✅ | ✅ | ✅ | 25 |
| ambiguous_2 | ambiguous | ❌ (got Other, want Bug) | ✅ | ❌ (got Data Export/Import, want Reporting & Analytics) | ✅ | ✅ | 60 |
| ambiguous_3 | ambiguous | ❌ (got Other, want Complaint) | ❌ (got Negative, want Neutral) | ❌ (got Other, want Reporting & Analytics) | ✅ | ✅ | 30 |
| dup_login_1 | duplicate_cluster | ✅ | ✅ | ✅ | ✅ | ✅ | 90 |
| dup_login_2 | duplicate_cluster | ✅ | ✅ | ✅ | ✅ | ✅ | 90 |
| dup_login_3 | duplicate_cluster | ✅ | ✅ | ✅ | ❌ (got High, want Critical) | ❌ (got Frustration, want Anger) | 90 |
| dup_crash_1 | duplicate_cluster | ✅ | ✅ | ✅ | ✅ | ✅ | 90 |
| dup_crash_2 | duplicate_cluster | ✅ | ✅ | ✅ | ✅ | ❌ (got Frustration, want Anger) | 90 |
| dup_crash_3 | duplicate_cluster | ✅ | ✅ | ✅ | ✅ | ✅ | 90 |
| contra_ui_1 | contradiction_pair | ✅ | ✅ | ✅ | ✅ | ✅ | 90 |
| contra_ui_2 | contradiction_pair | ✅ | ✅ | ✅ | ❌ (got Low, want Medium) | ✅ | 90 |
| contra_export_1 | contradiction_pair | ✅ | ✅ | ✅ | ✅ | ✅ | 90 |
| contra_export_2 | contradiction_pair | ✅ | ✅ | ✅ | ✅ | ✅ | 85 |