# Memory: working with Dr. Youssef El Masry

## Model routing (طلب يوسف)
Delegate every task to the subagent whose model fits its difficulty. The main agent plans, routes and talks to Youssef, and does trivial one-step actions itself.

| Subagent | Model | Use for |
|---|---|---|
| `opus-director` | Opus | Hardest tasks: full reel edit plans and second-by-second timelines, creative/motion direction, medical-accuracy and brand/legal review, complex pipelines, final quality review. |
| `sonnet-editor` | Sonnet | Medium tasks: executing approved edits with ffmpeg, captions and motion-graphics rendering, color correction, audio mastering, transcription cleanup, Gemini/Veo prompts, scripts/posts/captions drafts, website code. |
| `haiku-helper` | Haiku | Simple tasks: ffprobe, frames/contact sheets, renaming/converting files, cuts at given timestamps, link checks, hashtag lists. |

- Definitions live in `.claude/agents/`.
- If a subagent type is not loaded yet, use the Agent tool with `subagent_type: general-purpose` and `model: opus | sonnet | haiku` plus the same instructions.
- Run independent tasks in parallel.
- Always tell Youssef in one line which model handled what.

## Always
- Load the skill `anthropic-skills:rassam-elrashaka` before any work for Youssef.
- Reply in Egyptian Arabic.

## Transcription in cloud sessions
- huggingface.co is blocked, and Youssef declined opening it.
- Get Whisper Small from npm instead: `@skillninja/shortmovie-telop-model-p0..p3`. Run `npm pack` on each part, concatenate `model.bin.part0..3`, check the sha256 in p0, then run it with faster-whisper.
- Decode audio with ffmpeg to a numpy array. The pip build of faster-whisper fails when it opens files directly with av.
- mixkit.co is allowed for free music and sound effects.
