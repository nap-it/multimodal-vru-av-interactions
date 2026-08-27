# Online questionnaire

The questionnaire asked participants to imagine approaching or negotiating a crossing with an autonomous vehicle. It contained:

1. Demographics and the nine-item Affinity for Technology Interaction scale.
2. Clarity ratings and a forced ranking of six wearable-AR interfaces.
3. Applicability ratings and a forced ranking of five voice commands.
4. Applicability ratings and a forced ranking of nine gestures.
5. Three tasks pairing a voice command (Stop, Proceed, Slow Down) with one of nine gestures.
6. Optional open-ended feedback after each modality.

The importable LimeSurvey definitions and a human-readable outline are in `instrument/`. The exact recovered GIF, MP3, and overview-image files are in `stimuli/original_media/`; paper-facing static representations are in the other `stimuli/` subdirectories. The display ordering inside the survey did not match the item numbering later used in the manuscript; the authoritative mapping is documented in `docs/data_dictionary.md`.

## Data and analysis

`data/survey_responses_anonymized.csv` contains the minimized quantitative data. `data/open_ended_responses_anonymized.csv` contains the optional open-ended responses, with code definitions and response-level assignments in the adjacent codebook and audit files. Run:

```bash
python questionnaire/scripts/analyze_survey.py
```

The script writes full descriptive, omnibus, post-hoc, gesture-pairing, rating–ranking coherence, and exploratory sensitivity tables to `results/`.

## Scale and analysis details

- ATI items use a 1–6 scale; items 3, 6, and 8 are reverse scored.
- AR clarity and voice/gesture applicability use 1–7 ordinal scales.
- Repeated alternatives are compared with Friedman tests and Kendall’s W.
- Pairwise comparisons use two-sided Wilcoxon signed-rank tests with Holm correction within interaction family.
- Rankings are converted to preference scores (`k + 1 - rank`) before the Friedman/Wilcoxon analysis.
- Voice–gesture selections use chi-square goodness-of-fit tests against a uniform distribution and one-sided exact binomial tests against `p=1/9` for the expected semantic match.
- Rating–ranking coherence is the participant-level Spearman correlation between ratings and preference scores.
