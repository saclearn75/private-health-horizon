"""CLI entry point for the Private Health Horizon proof of concept."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from private_health_horizon.models import LiquidHFReasoner, RuleBasedLocalReasoner

DEFAULT_STATE = Path("data/private_patient_state.json")
SYNTHETIC_OBSERVATIONS = [
    {"day": 1, "resting_heart_rate": 62, "steps": 7600, "symptoms": [], "medication_confirmation": True},
    {"day": 2, "resting_heart_rate": 63, "steps": 7350, "symptoms": [], "medication_confirmation": True},
    {"day": 3, "resting_heart_rate": 72, "steps": 4100, "symptoms": ["fatigue"], "medication_confirmation": True},
]


def load_state(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {"observations": [], "analyses": []}


def make_public_query(analysis: dict[str, Any], observations: list[dict[str, Any]]) -> str | None:
    if not (
        analysis.get("meaningful_change_detected")
        and analysis.get("external_information_would_be_useful")
        and len(observations) >= 2
    ):
        return None
    baseline, latest = observations[0], observations[-1]
    concepts: list[str] = []
    new_symptoms = [symptom for symptom in latest["symptoms"] if symptom not in baseline["symptoms"]]
    if new_symptoms:
        concepts.append("new " + " and ".join(new_symptoms))
    if latest["resting_heart_rate"] - baseline["resting_heart_rate"] >= 8:
        concepts.append("increased resting heart rate")
    if baseline["steps"] - latest["steps"] >= 2500:
        concepts.append("reduced activity")
    return "general information about " + " associated with ".join(concepts) if concepts else None


def validate_public_query(query: str | None, observations: list[dict[str, Any]]) -> None:
    if query is None:
        return
    if any(character.isdigit() for character in query):
        raise ValueError("Public query leaked an exact numeric value.")
    if "medication" in query.lower():
        raise ValueError("Public query leaked medication information.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Local-only synthetic longitudinal health demo")
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--reasoner", choices=("fallback", "liquid"), default="fallback")
    args = parser.parse_args()
    state = load_state(args.state)
    reasoner = RuleBasedLocalReasoner() if args.reasoner == "fallback" else LiquidHFReasoner()
    args.state.parent.mkdir(parents=True, exist_ok=True)

    for observation in SYNTHETIC_OBSERVATIONS:
        if observation in state["observations"]:
            continue
        state["observations"].append(observation)
        print(f"Running local reasoning for synthetic day {observation['day']}...", flush=True)
        analysis = reasoner.analyze(state["observations"])
        public_query = make_public_query(analysis, state["observations"])
        validate_public_query(public_query, state["observations"])
        state["analyses"].append({"day": observation["day"], "analysis": analysis, "public_query": public_query})
        print("\nPRIVATE INPUT (local only)")
        print(json.dumps(observation, indent=2))
        print("LOCAL REASONING")
        print(json.dumps(analysis, indent=2))
        print("UPDATED PRIVATE STATE")
        print(f"Stored locally in {args.state}")
        print("PRIVACY-SAFE PUBLIC QUERY (printed only; never sent)")
        print(public_query or "No external information requested.")

    args.state.write_text(json.dumps(state, indent=2) + "\n")


if __name__ == "__main__":
    main()
