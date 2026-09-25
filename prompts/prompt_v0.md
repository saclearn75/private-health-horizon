Create a minimal Python prototype called Private Health Horizon.

GOAL
Build a desktop proof-of-concept for a privacy-preserving, long-horizon healthcare agent using a Liquid AI model locally.

This is a hackathon prototype. Optimize for simplicity, inspectability, and a working demo rather than production architecture.

IMPORTANT CONSTRAINTS

1. Patient data must remain local.
2. Do not send patient data to any external API.
3. Use synthetic patient data only.
4. Do not implement diagnosis or medical treatment recommendations.
5. External web retrieval will be added later. Do NOT implement it yet.
6. Keep components modular so Nimble retrieval can be added later.
7. Prefer a simple Python CLI initially. Do not build a web UI yet.
8. Provide instructions on running the demo.  

MODEL

Use a suitable Liquid AI LFM model available through Hugging Face. Prefer a small model that can reasonably run locally on a laptop.

Create the model integration behind a simple interface so the specific Liquid model can be changed later.

DATA

Create synthetic longitudinal observations for a fictional patient.

Each observation should contain:

- day
- resting heart rate
- steps
- symptoms
- medication confirmation

Store the data locally as JSON.

AGENT BEHAVIOR

The application processes observations sequentially.

For each new observation:

1. Load previous patient state.
2. Add the new observation.
3. Ask the local Liquid model to reason about changes over time.
4. Produce structured output containing:

   - summary of recent trend
   - important changes from baseline
   - whether a meaningful change was detected
   - whether external information would be useful
   - a privacy-safe external search query if external information
     would be useful

5. Save updated state locally.

PRIVACY

Create a clear boundary between:

A. PRIVATE STATE
   Raw patient observations and longitudinal context.

B. PUBLIC QUERY
   A sanitized query that could safely be sent to an external
   web-search provider.

The public query must not contain:
- patient name
- identifiers
- complete patient history
- exact private record contents

For now, PRINT the proposed public query but do not send it anywhere.

OBSERVABILITY

Print enough information to demonstrate:

PRIVATE INPUT
-> LOCAL LIQUID REASONING
-> UPDATED PRIVATE STATE
-> PRIVACY-SAFE PUBLIC QUERY

Create a README explaining the architecture and how to run it.

Before writing significant code, inspect the environment and propose the smallest implementation plan. Then implement one milestone at a time.