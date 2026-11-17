# Memory: working with Dr. Youssef El Masry

## Model routing (طلب يوسف)
Delegate every task to the subagent whose model fits its difficulty. The main agent plans, routes and talks to Youssef, and does trivial one-step actions itself.

| Subagent | Model | Use for |
|---|---|---|
| `opus-director` | Opus | Hardest tasks: full reel edit plans and second-by-second timelines, creative/motion direction, medical-accuracy and brand/legal review, complex pipelines, final quality review. |
| `sonnet-editor` | Sonnet | Medium tasks: executing approved edits with ffmpeg, captions and motion-graphics rendering, color correction, audio mastering, transcription cleanup, Gemini/Veo prompts, scripts/posts/captions drafts, website code. |
| `haiku-helper` | Haiku | Simple tasks: ffprobe, frames/contact sheets, renaming/converting files, cuts at given timestamps, link checks, hashtag lists. |

- **Budget rule (Youssef, Nov 2026): Opus is the exception, not the default.** One reel used about 10% of his credit, which is too much.
  - Use `opus-director` only for an extremely important task that cannot reach top quality on any other model, such as a full reel plan for a new format, or a high-risk medical or legal review. Otherwise use it only when Youssef asks for it by name.
  - Everything else goes to Sonnet: edit plans for a known format, renders, QC reviews, scripts, prompts and code.
  - Mechanical work goes to Haiku: probes, frames, conversions, downloads, sheets.
  - Keep the main session on Sonnet.
  - Save tokens: don't read large files or images unless they are needed, use small contact sheets, and keep subagent reports short.
- Definitions live in `.claude/agents/`.
- If a subagent type is not loaded yet, use the Agent tool with `subagent_type: general-purpose` and `model: opus | sonnet | haiku` plus the same instructions.
- Run independent tasks in parallel.
- Always tell Youssef in one line which model handled what.

## Always
- Load the skill `anthropic-skills:rassam-elrashaka` before any work for Youssef.
- Reply in Egyptian Arabic.

## Reel toolkit (rebuild first in every new session)
- Run `bash tools/reel-toolkit/setup.sh` (default dir `~/reel-toolkit`). It is tested end to end and installs:
  - Python audio and video libs;
  - GSAP, lottie and anime.js;
  - Google fonts (Zain and alternatives);
  - Whisper Small;
  - 42 Mixkit sounds and tracks, from `manifest.csv`;
  - 6 brand transitions (navy_wipe, gold_light_sweep, whip_blur_mask, circle_iris_gold, split_bars, particle_dissolve).
- After setup, render the transitions with `node transitions/render.js && python3 transitions/to_rgba.py`.
- `tools/reel-toolkit/presets.sh` holds the grade, voice-chain, punch-in, xfade and export presets.
- Grade for the insulin-resistance shoot (grey wall, green shirt): use `GRADE_CINEMATIC`.
- Load the skills `talking-head-reel-editor` and `professional-cinematic-video-enhancer` before editing.
- Music picks need Youssef's approval. The audition file is numbered 1–8 in manifest order.

## Transcription in cloud sessions
- huggingface.co is blocked, and Youssef declined opening it.
- Get Whisper Small from npm instead: `@skillninja/shortmovie-telop-model-p0..p3`. Run `npm pack` on each part, concatenate `model.bin.part0..3`, check the sha256 in p0, then run it with faster-whisper.
- Decode audio with ffmpeg to a numpy array. The pip build of faster-whisper fails when it opens files directly with av.
- mixkit.co is allowed for free music and sound effects.
