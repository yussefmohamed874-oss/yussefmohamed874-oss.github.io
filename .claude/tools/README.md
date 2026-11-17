# montage-tools
Run from anywhere: /home/user/montage-tools/mt <command>
  probe <video>            stream info (JSON)
  extract <video>          16k mono WAV -> work/ (same timeline as the video)
  transcribe <video> [--lang ar] [--prompt "domain words"]   -> out/<name>.{json,txt,srt} (word + segment times)
  silence <file> [--noise -35] [--min 0.4]                    -> out/<name>.silence.json
  cuts <video> [--max-pause 0.5 --keep 0.4 --pad 0.12 --lead 0.15 --tail 0.3]  -> out/<name>.cuts.json (proposal, approved=false)
  apply <cuts.json>        needs "approved": true; writes work/<name>.edit.mp4 + out/<name>.edit.{json,srt}. Originals are never touched.
Model: models/whisper-small-ct2-int8 (third-party CT2 conversion of OpenAI Whisper small). Review all Arabic text manually.
