# Multimodal bidirectional pedestrian–AV interaction study materials

This repository accompanies **“Evaluating Strategies for Multimodal Bidirectional Interactions between Pedestrians and AVs.”** It contains the materials needed to inspect and reproduce the paper’s online-questionnaire statistics and controlled speech-pipeline benchmarks.

## Contents

- `questionnaire/`: LimeSurvey instrument, original survey media, anonymized quantitative and open-ended responses, coding audit, analysis code, and generated tables.
- `benchmarks/`: sanitized latency measurements, evaluation audio, ASR references and hypotheses, analysis code, and generated summaries.
- `docs/`: data dictionary.

## Reproduce the results

Python 3.9 or newer is required.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python run_all.py
```

The command regenerates `questionnaire/results/` and `benchmarks/results/`, then checks the headline values and released-data integrity. It does not download data or contact external services.

## Data-release status

The quantitative survey table contains only new participant IDs, broad demographics, ordinal responses, ranks, and categorical pairing selections. LimeSurvey response IDs, dates, timing telemetry, recruitment-source fields, and profession were removed. Open-ended responses are released separately with the same randomized IDs; internal author annotations were removed, while participant text was otherwise preserved.

## Citation and licensing

The authors' original repository material is licensed under GPL-3.0. Third-party material retains its own terms, including CC BY 4.0 for FLEURS and CC BY-NC 3.0 for UrbanSound8K-derived audio. See [`LICENSE`](LICENSE), [`LICENSES/README.md`](LICENSES/README.md), and [`THIRD_PARTY.md`](THIRD_PARTY.md). Citation metadata are in [`CITATION.cff`](CITATION.cff).
