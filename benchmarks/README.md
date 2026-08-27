# Controlled interaction-system benchmarks

This directory reproduces the paper’s technical evaluation.

## Released evidence

- HoloLens 2 microphone-stream latency over wired and Wi‑Fi connections.
- Whisper transcription latency for the infrastructure-assisted Turbo configuration and five local Jetson configurations.
- Complete infrastructure-assisted packet components needed for the representative end-to-end decomposition.
- Controlled-command references and ASR hypotheses for clean and urban-noise conditions.
- FLEURS `en_us` test references and hypotheses for the two reported configurations.
- The TTS-generated controlled command track, a version with leading silence, the UrbanSound8K-derived noise track, and the mixed noisy-command track used by the benchmark.

## Reproduce

```bash
python benchmarks/scripts/analyze_benchmarks.py
```

Text is lowercased, punctuation is removed, repeated whitespace is collapsed, and edit counts are accumulated across aligned utterance pairs.

Wake words are `vehicle`, `car`, `self-driving car`, and `self driving car`, matched with word boundaries. The controlled corpus contains 31 wake-word-positive and 107 wake-word-negative commands.

## Audio files

The audio in `data/audio/` is supplied to document the evaluation input:

- `controlled_commands.mp3`: TTS-generated command sequence.
- `controlled_commands_with_leading_silence.mp3`: command sequence with the test's leading silence.
- `urban_noise_track.mp3`: concatenated and normalized UrbanSound8K background excerpts.
- `controlled_commands_with_urban_noise.mp3`: command sequence mixed with the noise track at varying SNRs.

The TTSMaker-generated files may be used under TTSMaker's generated-audio terms. The two files containing UrbanSound8K material remain subject to CC BY-NC 3.0 and therefore cannot be used commercially. See the root `THIRD_PARTY.md` and `LICENSES/README.md`.
