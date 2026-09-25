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


def make_public_query(analysis: dict[str, Any]) -> str | None:
    if not analysis.get("external_information_would_be_useful"):
        return None
    return "general educational material about changing wellbeing and activity patterns"


def validate_public_query(query: str | None, observations: list[dict[str, Any]]) -> None:
    if query is None:
        return
    def scalars(value: Any) -> list[str]:
        if isinstance(value, dict):
            return [item for nested in value.values() for item in scalars(nested)]
        if isinstance(value, list):
            return [item for nested in value for item in scalars(nested)]
        return [str(value).lower()] if isinstance(value, (str, int, float, bool)) else []

    forbidden = [item for observation in observations for item in scalars(observation)]
    if any(value and value in query.lower() for value in forbidden):
        raise ValueError("Public query leaked private observation content.")


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
        public_query = make_public_query(analysis)
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
