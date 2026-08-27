# Data dictionary

## Questionnaire responses

File: `questionnaire/data/survey_responses_anonymized.csv`

| Field | Meaning |
|---|---|
| `participant_id` | New release-only identifier; does not preserve a LimeSurvey ID or row order. |
| `language` | Questionnaire language (`pt`, `en`). |
| `age_group` | Self-reported age bin. |
| `gender` | Self-reported gender normalized to `male` or `female` (the only observed categories). |
| `ATI_1`–`ATI_9` | Scored 1–6 Affinity for Technology Interaction items; reverse-keyed items are already reversed. |
| `rating_I*` | AR-interface clarity rating, 1–7. |
| `rating_C*` | Voice-command applicability rating, 1–7. |
| `rating_G*` | Gesture applicability rating, 1–7. |
| `rank_I*`, `rank_C*`, `rank_G*` | Rank position; 1 is most preferred. |
| `pair_stop`, `pair_proceed`, `pair_slow_down` | Manuscript gesture ID selected to accompany the named voice command. |

## Open-ended responses

File: `questionnaire/data/open_ended_responses_anonymized.csv`

| Field | Meaning |
|---|---|
| `participant_id` | Same release-only ID used in the quantitative table. |
| `modality` | Prompt family: `AR`, `Voice`, or `Gesture`. |
| `response_language` | Questionnaire language in which the response was submitted. |
| `response_text` | Participant text with internal author annotations removed; otherwise unchanged. |

`open_ended_codebook.csv` defines the reported qualitative categories. `open_ended_code_assignments.csv` links responses to zero or more categories. See `OPEN_ENDED_CODING.md` for provenance.

### Item identifiers

| ID | Label |
|---|---|
| I1 | Yielding to Cross |
| I2 | Vehicle Approaching |
| I3 | Directional Arrow |
| I4 | Green Traffic Light |
| I5 | Red Traffic Light |
| I6 | Projected Crosswalk |
| C1 | Stop |
| C2 | Proceed |
| C3 | Avoid Obstacle |
| C4 | Slow Down |
| C5 | Wait for Pedestrians |
| G1 | Avoid Obstacle |
| G2 | Emergency Stop |
| G3 | Follow Me |
| G4 | Go Back |
| G5 | T-Pose |
| G6 | Proceed |
| G7 | Slow Down |
| G8 | Stop |
| G9 | Wait for Pedestrians |

## Benchmark measurements and audio

- `microphone_latency.csv`: connection type, release-only replicate ID, stream latency, and receiver-side processing time.
- `transcription_latency.csv`: computing placement, model, release-only replicate ID, and Whisper transcription time.
- `vm_e2e_components.csv`: complete infrastructure-assisted RTT, transcription, intent-recognition, and communication measurements.
- `commands/` and `fleurs/`: references and ASR hypotheses used to compute WER/CER.
- `audio/`: TTS command input and UrbanSound8K-derived noise/mixed input. See `THIRD_PARTY.md` for non-commercial restrictions on the latter files.
