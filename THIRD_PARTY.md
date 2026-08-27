# Third-party materials

## FLEURS

`benchmarks/data/fleurs/reference/en_us_test.txt` contains the reference transcriptions used from the FLEURS `en_us` test split. FLEURS is published by Google under CC BY 4.0; cite:

> Conneau, A., Ma, M., Khanuja, S., Zhang, Y., Axelrod, V., Dalmia, S., Riesa, J., Rivera, C., & Bapna, A. (2022). FLEURS: Few-shot Learning Evaluation of Universal Representations of Speech. arXiv:2205.12446.

Dataset card: <https://huggingface.co/datasets/google/fleurs>

No FLEURS audio is included.

## TTSMaker

`benchmarks/data/audio/controlled_commands.mp3` and `controlled_commands_with_leading_silence.mp3` were generated with TTSMaker. TTSMaker's generated-audio terms grant users a non-exclusive, irrevocable, worldwide, and perpetual license to use generated audio and state that TTSMaker does not claim ownership of the specific generated content.

Terms checked 2026-08-27: <https://ttsmaker.com/copyright_and_commercial_license_terms>

## UrbanSound8K

`benchmarks/data/audio/urban_noise_track.mp3` is derived from background excerpts in UrbanSound8K. `controlled_commands_with_urban_noise.mp3` combines that derivative track with the controlled TTS commands. Both files remain subject to the Creative Commons Attribution-NonCommercial 3.0 license and may not be used commercially.

Dataset compiled by Justin Salamon, Christopher Jacoby, and Juan Pablo Bello. Please cite:

> Salamon, J., Jacoby, C., & Bello, J. P. (2014). A Dataset and Taxonomy for Urban Sound Research. Proceedings of the 22nd ACM International Conference on Multimedia, 1041–1044. <https://doi.org/10.1145/2647868.2655045>

Dataset and license information: <https://urbansounddataset.weebly.com/urbansound8k.html>

The original local metadata and `FREESOUNDCREDITS.txt` were not retained with the derived track, so the exact underlying Freesound clip IDs could not be reconstructed. The repository therefore supplies dataset-level attribution but cannot provide a per-clip credit ledger.

## Questionnaire media

The recovered GIFs, MP3 prompts, and overview images in `questionnaire/stimuli/original_media/` were supplied by the study authors. Their original repository material is covered by the root GPL-3.0 license.

## LimeSurvey

The `.lss` and `.xml` files are instrument exports. LimeSurvey application code and themes are not included.
