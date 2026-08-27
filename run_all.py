#!/usr/bin/env python3
"""Regenerate public results and run deterministic release checks."""

from __future__ import annotations

import json
import math
import re
import subprocess
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
COMMANDS = (
    [sys.executable, str(ROOT / "questionnaire/scripts/analyze_survey.py")],
    [sys.executable, str(ROOT / "benchmarks/scripts/analyze_benchmarks.py")],
)

EXPECTED_MEDIA = {
    "AR.png", "Avoid-Obstacle.gif", "Emergency-Stop.gif", "Follow.gif",
    "Gesturing.png", "Gesturing_and_Speaking.png", "Go-Back.gif",
    "Proceed.gif", "Slow-Two-Hands.gif", "Speaking.png", "Stop.gif",
    "T-Pose.gif", "Wait-Pedestrians.gif", "obstacle_new.mp3",
    "pedestrians_new.mp3", "proceed_new.mp3", "slow_down.mp3", "stop.mp3",
}


def verify_release() -> None:
    survey = pd.read_csv(ROOT / "questionnaire/data/survey_responses_anonymized.csv")
    assert survey.shape == (124, 56)
    assert survey.participant_id.nunique() == 124
    assert survey.language.value_counts().to_dict() == {"pt": 117, "en": 7}

    responses = pd.read_csv(ROOT / "questionnaire/data/open_ended_responses_anonymized.csv")
    assert responses.groupby("modality").size().to_dict() == {"AR": 29, "Gesture": 16, "Voice": 13}
    released_text = "\n".join(responses.response_text.astype(str))
    for pattern in (
        r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",
        r"https?://|www\.",
        r"(?<!\d)(?:\+?\d[\d ()-]{7,}\d)(?!\d)",
        r"NOTA ANDRÉ",
    ):
        assert not re.search(pattern, released_text, flags=re.I)

    codebook = pd.read_csv(ROOT / "questionnaire/data/open_ended_codebook.csv").set_index("code")
    assignments = pd.read_csv(ROOT / "questionnaire/data/open_ended_code_assignments.csv")
    counts = assignments.code.value_counts()
    assert counts.to_dict() == codebook.manuscript_count.astype(int).to_dict()
    assert set(assignments.participant_id) <= set(responses.participant_id)

    e2e = json.loads((ROOT / "benchmarks/results/e2e_latency_summary.json").read_text())
    assert math.isclose(e2e["infrastructure_assisted_turbo_ms"], 440.0364737808095)
    assert math.isclose(e2e["local_base_ms"], 365.6273285238142)

    media_dir = ROOT / "questionnaire/stimuli/original_media"
    assert EXPECTED_MEDIA <= {path.name for path in media_dir.iterdir() if path.is_file()}
    audio_dir = ROOT / "benchmarks/data/audio"
    assert {"controlled_commands.mp3", "controlled_commands_with_leading_silence.mp3", "controlled_commands_with_urban_noise.mp3", "urban_noise_track.mp3"} <= {path.name for path in audio_dir.iterdir() if path.is_file()}
    assert (ROOT / "LICENSE").read_text().lstrip().startswith("GNU GENERAL PUBLIC LICENSE")
    print("PASS: quantitative results, open-ended data/coding, media, audio, and license checks")


def main() -> None:
    for command in COMMANDS:
        subprocess.run(command, cwd=ROOT, check=True)
    verify_release()


if __name__ == "__main__":
    main()
