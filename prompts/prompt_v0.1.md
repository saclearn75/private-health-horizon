The real local Liquid model is now working. Freeze the current architecture.

Make a minimal v0.1 improvement to the Liquid reasoning prompt only.
Do not add Nimble, FHIR, Android, a UI, or new dependencies.

Problems observed:
1. Day 1 described an "increase" despite having only one observation.
2. Day 2 incorrectly described steps as increasing when they fell from 7600 to 7350.
3. The model marked meaningful_change_detected=true and external_information_would_be_useful=true even for Day 1.

Update the Liquid prompt so that:

- It reasons only from observations actually supplied.
- With one observation, it explicitly states that there is insufficient longitudinal history to identify a trend.
- It compares numeric values accurately.
- Small changes should not automatically be considered meaningful.
- external_information_would_be_useful should only be true when a meaningful longitudinal change warrants outside information.
- Do not make diagnoses or treatment recommendations.
- Preserve the existing privacy boundary and output schema.
- Preserve local Liquid inference.
- Do not silently use the fallback reasoner.

PUBLIC QUERY GENERATION

The privacy-safe public query must be dynamically generated from the
meaningful change detected in the current longitudinal state.

Do not use a fixed generic query.

For example, if the meaningful change consists of new fatigue,
increased resting heart rate, and reduced activity, an acceptable
query would be:

"general information about new fatigue associated with increased
resting heart rate and reduced activity"

The public query may contain generalized clinical concepts needed
for useful retrieval, but must not contain:
- patient identifiers
- exact vital-sign values
- exact step counts
- complete longitudinal history
- medication information unless explicitly required by a future
  privacy policy
- diagnoses inferred by the model

If no meaningful longitudinal change is detected, public_query must be null.

Also ensure boolean fields are actual JSON booleans, not strings such as "Yes".

After making the change, run the same 3-day synthetic dataset using --reasoner liquid and show me the resulting state.

Finally update the README Build Status:

v-1:
- Nimble direct API smoke test
- Liquid model smoke test

v0:
- Local synthetic patient timeline
- Local Liquid LFM2.5-1.2B-Instruct inference
- Persistent longitudinal private state
- Privacy-safe public query generation

v0.1:
- Improved longitudinal reasoning prompt
- Accurate baseline/trend handling
- External retrieval gated on meaningful change

Planned:
- v1: Nimble retrieval integration
- v1.1: FHIR-ready escalation package
- v2: Android edge deployment
- v3: wearable/smartwatch input



