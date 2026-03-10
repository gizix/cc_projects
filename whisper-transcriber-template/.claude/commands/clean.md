---
description: Remove temporary extracted audio files from the tmp/ directory
---

Clean up temporary audio files created during transcription.

Steps:
1. Check if the `./tmp/` directory exists
2. List any `*_audio.wav` files found there
3. Ask the user to confirm before deleting (unless the directory is obviously safe to clear)
4. Remove the temporary files: delete all `*_audio.wav` files in `./tmp/`
5. Report how many files were removed

Also check for any stray `*_audio.wav` files in the current directory and offer to remove them.

Note: Transcripts (`.txt`, `.srt`, `.vtt`, `.json`) are NOT removed by this command — only temporary WAV audio files used as intermediate processing artifacts.
