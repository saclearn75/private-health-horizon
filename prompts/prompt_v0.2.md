The v0.1 Liquid prompt is now too conservative.

Do not change the architecture, model, dataset, or add features.
Modify only the Liquid reasoning prompt/output constraints.

Observed behavior:
- Day 1 correctly reports insufficient longitudinal history.
- Day 2 also reports insufficient longitudinal history.
- Day 3 incorrectly reports insufficient longitudinal history despite
  having three observations.
- Day 3 fails to recognize the combination of increased resting heart
  rate, substantially reduced activity, and newly appearing fatigue.
- external_information_would_be_useful is true even when
  meaningful_change_detected is false.

Correct the reasoning instructions as follows:

LONGITUDINAL REASONING

1. One observation:
   This establishes a baseline only.
   meaningful_change_detected must be false.
   external_information_would_be_useful must be false.
   public_query must be null.

2. Two observations:
   Compare them numerically.
   Small differences may be described, but should not automatically
   constitute a meaningful longitudinal change.

3. Three or more observations:
   Evaluate the trajectory across all available observations.
   Consider multiple signals together, including:
   - direction and magnitude of resting-heart-rate change
   - direction and magnitude of activity/step change
   - appearance of a new symptom

   A combination of materially changed physiological/activity signals
   plus a newly appearing symptom can constitute a meaningful
   longitudinal change even though no diagnosis can be inferred.

For the existing synthetic dataset, do NOT hard-code the expected
answer or exact numerical thresholds. The model should reason from
the supplied observations.

CONSISTENCY RULES

If meaningful_change_detected is false:
- external_information_would_be_useful must be false
- public_query must be null

If meaningful_change_detected is true and outside information would
help interpret the change:
- external_information_would_be_useful may be true
- generate a privacy-safe public_query dynamically from the detected
  changes

The query should describe generalized concepts such as:
"new fatigue with increased resting heart rate and reduced activity"

It must not include exact patient measurements, identifiers, complete
history, medication information, or an inferred diagnosis.

Continue using actual JSON booleans.

Run the same three-day dataset again using the local Liquid reasoner.
Do not use fallback.