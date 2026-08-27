#!/usr/bin/env python3
"""Reproduce latency, WER/CER, and wake-word results from released data."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pandas as pd


WAKE_WORDS = ("vehicle", "car", "self-driving car", "self driving car")
COMMAND_CONFIGURATIONS = (
    "vm", "jetson_tiny", "jetson_base", "jetson_small", "jetson_medium",
    "jetson_turbo", "vm_noise", "jetson_base_noise",
)


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").strip().splitlines()


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", "", text.lower())).strip()


def edit_distance(reference: list[str] | str, hypothesis: list[str] | str) -> int:
    previous = list(range(len(hypothesis) + 1))
    for row, reference_item in enumerate(reference, start=1):
        current = [row]
        for column, hypothesis_item in enumerate(hypothesis, start=1):
            current.append(min(current[-1] + 1, previous[column] + 1, previous[column - 1] + (reference_item != hypothesis_item)))
        previous = current
    return previous[-1]


def error_rates(reference: list[str], hypothesis: list[str]) -> tuple[float, float]:
    if len(reference) != len(hypothesis):
        raise ValueError(f"Reference/hypothesis line mismatch: {len(reference)} != {len(hypothesis)}")
    reference = [normalize(line) for line in reference]
    hypothesis = [normalize(line) for line in hypothesis]
    word_errors = sum(edit_distance(r.split(), h.split()) for r, h in zip(reference, hypothesis))
    character_errors = sum(edit_distance(r, h) for r, h in zip(reference, hypothesis))
    return 100 * word_errors / sum(len(line.split()) for line in reference), 100 * character_errors / sum(len(line) for line in reference)


def has_wake_word(text: str) -> bool:
    return any(re.search(r"\b" + re.escape(word) + r"\b", text.lower()) for word in WAKE_WORDS)


def recognition_tables(data_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    command_reference = read_lines(data_dir / "commands" / "reference" / "commands.txt")
    metric_rows, wake_rows = [], []
    for configuration in COMMAND_CONFIGURATIONS:
        hypothesis = read_lines(data_dir / "commands" / "hypotheses" / f"{configuration}.txt")
        wer, cer = error_rates(command_reference, hypothesis)
        condition = "noise" if configuration.endswith("_noise") else "controlled commands"
        metric_rows.append({"configuration": configuration, "condition": condition, "wer_pct": wer, "cer_pct": cer})
        tp = fn = fp = tn = 0
        for reference, candidate in zip(command_reference, hypothesis):
            expected, detected = has_wake_word(reference), has_wake_word(candidate)
            if expected and detected: tp += 1
            elif expected: fn += 1
            elif detected: fp += 1
            else: tn += 1
        wake_rows.append({
            "configuration": configuration, "tp": tp, "fn": fn, "fp": fp, "tn": tn,
            "detection_pct": 100 * tp / (tp + fn), "false_positive_pct": 100 * fp / (fp + tn),
        })

    fleurs_reference = read_lines(data_dir / "fleurs" / "reference" / "en_us_test.txt")
    for configuration in ("vm", "jetson_base"):
        hypothesis = read_lines(data_dir / "fleurs" / "hypotheses" / f"{configuration}.txt")
        wer, cer = error_rates(fleurs_reference, hypothesis)
        metric_rows.append({"configuration": configuration, "condition": "FLEURS en_us test", "wer_pct": wer, "cer_pct": cer})
    return pd.DataFrame(metric_rows), pd.DataFrame(wake_rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path(__file__).resolve().parents[1] / "data")
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "results")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    mic = pd.read_csv(args.data / "microphone" / "microphone_latency.csv")
    mic_summary = mic.groupby("connection").latency_ms.agg(["count", "mean", "std", "median", "min", "max"]).reset_index()
    transcription = pd.read_csv(args.data / "transcription_latency.csv")
    transcription_summary = transcription.groupby(["configuration", "placement", "model"]).transcription_ms.agg(["count", "mean", "std"]).reset_index()
    vm = pd.read_csv(args.data / "vm_e2e_components.csv")
    recognition, wake = recognition_tables(args.data)

    wifi_mean = mic.loc[mic.connection == "wifi", "latency_ms"].mean()
    rasa_mean = vm.intent_ms.mean()
    vm_total = wifi_mean + vm.communication_ms.mean() + vm.transcription_ms.mean() + rasa_mean
    local_base_mean = transcription.loc[transcription.configuration == "jetson_base", "transcription_ms"].mean()
    local_total = wifi_mean + local_base_mean + rasa_mean
    e2e = {
        "infrastructure_assisted_turbo_ms": vm_total,
        "local_base_ms": local_total,
        "wifi_microphone_ms": wifi_mean,
        "vm_communication_ms": vm.communication_ms.mean(),
        "vm_transcription_ms": vm.transcription_ms.mean(),
        "intent_recognition_ms": rasa_mean,
    }

    mic_summary.to_csv(args.output / "microphone_latency_summary.csv", index=False)
    transcription_summary.to_csv(args.output / "transcription_latency_summary.csv", index=False)
    recognition.to_csv(args.output / "recognition_error_rates.csv", index=False)
    wake.to_csv(args.output / "wake_word_metrics.csv", index=False)
    (args.output / "e2e_latency_summary.json").write_text(json.dumps(e2e, indent=2), encoding="utf-8")
    print(json.dumps(e2e, indent=2))


if __name__ == "__main__":
    main()
