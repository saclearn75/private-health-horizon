"""Local reasoning adapters. No adapter sends patient data over the network."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any


class LocalReasoner(ABC):
    @abstractmethod
    def analyze(self, observations: list[dict[str, Any]]) -> dict[str, Any]:
        """Return a structured longitudinal observation, not medical advice."""


class RuleBasedLocalReasoner(LocalReasoner):
    """Offline demo fallback that keeps the prototype runnable without model weights."""

    def analyze(self, observations: list[dict[str, Any]]) -> dict[str, Any]:
        baseline, latest = observations[0], observations[-1]
        heart_rate_delta = latest["resting_heart_rate"] - baseline["resting_heart_rate"]
        steps_delta = latest["steps"] - baseline["steps"]
        symptoms_changed = latest["symptoms"] != baseline["symptoms"]
        meaningful_change = abs(heart_rate_delta) >= 8 or abs(steps_delta) >= 2500 or symptoms_changed
        return {
            "summary_of_recent_trend": f"Across {len(observations)} local observations, resting heart rate changed by {heart_rate_delta:+d} bpm and steps changed by {steps_delta:+d}.",
            "important_changes_from_baseline": {"resting_heart_rate_delta_bpm": heart_rate_delta, "steps_delta": steps_delta, "symptoms_changed": symptoms_changed, "medication_confirmation": latest["medication_confirmation"]},
            "meaningful_change_detected": meaningful_change,
            "external_information_would_be_useful": meaningful_change and bool(latest["symptoms"]),
            "reasoning_mode": "offline rule-based demo fallback",
        }


class LiquidHFReasoner(LocalReasoner):
    """Runs an open-weight Liquid model locally through Transformers."""

    def __init__(self, model_id: str = "LiquidAI/LFM2.5-1.2B-Instruct") -> None:
        self.model_id, self._tokenizer, self._model = model_id, None, None

    def _load(self) -> None:
        if self._model is not None:
            return
        from transformers import AutoModelForCausalLM, AutoTokenizer
        self._tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        self._model = AutoModelForCausalLM.from_pretrained(self.model_id, device_map="auto")

    def analyze(self, observations: list[dict[str, Any]]) -> dict[str, Any]:
        self._load()
        prompt = """Return compact JSON only, with exactly these keys:
summary_of_recent_trend, important_changes_from_baseline,
meaningful_change_detected, external_information_would_be_useful.
The two final fields must be JSON booleans, never strings.

Reason only from the supplied synthetic observations. Do not diagnose or recommend treatment.
With exactly one observation, it establishes a baseline only: explicitly state there is
insufficient longitudinal history to identify a trend, and set both boolean fields to false.
With exactly two observations, compare their numeric values accurately. Small differences may
be described but do not automatically constitute a meaningful longitudinal change.
With three or more observations, evaluate the trajectory across all supplied observations.
Consider the direction and magnitude of resting-heart-rate change, activity/step change, and
the appearance of new symptoms together. A combination of materially changed physiological or
activity signals plus a new symptom can be a meaningful longitudinal change, without inferring
a diagnosis. Do not hard-code an expected answer or numeric threshold.

Consistency rules: if meaningful_change_detected is false, then
external_information_would_be_useful must be false. Set
external_information_would_be_useful true only when a meaningful longitudinal change warrants
general outside information. Keep the summary and changes factual and short.

Synthetic observations:
""" + json.dumps(observations)
        inputs = self._tokenizer.apply_chat_template(
            [{"role": "user", "content": prompt}],
            add_generation_prompt=True,
            return_dict=True,
            return_tensors="pt",
        ).to(self._model.device)
        output = self._model.generate(**inputs, max_new_tokens=128, do_sample=False)
        result = json.loads(
            self._tokenizer.decode(output[0][inputs["input_ids"].shape[-1]:], skip_special_tokens=True)
        )
        for field in ("meaningful_change_detected", "external_information_would_be_useful"):
            if not isinstance(result.get(field), bool):
                raise ValueError(f"Liquid model returned a non-boolean {field}.")
        result["reasoning_mode"] = f"local Liquid model: {self.model_id}"
        return result
