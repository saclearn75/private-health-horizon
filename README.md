# Private Health Horizon

A local-only CLI proof of concept for a long-horizon health-observation agent. It uses **synthetic data only** and produces observations of changes over time; it does not diagnose or recommend treatment.

## Privacy boundary

```
synthetic observations -> private local JSON state -> local reasoning -> sanitized public query
                                                               -> printed only (not retrieved)
```

Raw observations and accumulated state stay in `data/private_patient_state.json`. The public-query generator emits broad educational wording and validates that no exact private scalar or text value appears in it. Nimble is intentionally not called.

## Run

The fallback requires no dependencies and demonstrates persistence and the privacy flow:

```powershell
py -3.14 -m private_health_horizon.app --reasoner fallback
```

For local Liquid inference, install a CPU-capable PyTorch build compatible with your Python version, then install the remaining dependencies:

```powershell
py -3.14 -m pip install -r requirements.txt
py -3.14 -m private_health_horizon.app --reasoner liquid
```

The adapter defaults to `LiquidAI/LFM2.5-1.2B-Instruct`. Hugging Face may download model weights before any synthetic record is supplied; subsequent inference is local. Change `model_id` in `LiquidHFReasoner` to test another Liquid model.

## Components

- `private_health_horizon/app.py`: sequential processing, state storage, and CLI output.
- `private_health_horizon/models.py`: swappable local-reasoning boundary.
- `data/private_patient_state.json`: generated private state (ignored by Git).

`make_public_query` is the explicit future Nimble integration boundary; it only prints a safe query today.
