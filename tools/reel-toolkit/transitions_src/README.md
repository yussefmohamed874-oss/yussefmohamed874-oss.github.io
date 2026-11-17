# Dr. Youssef El Masry - Brand Transitions (1080x1920, 30 fps, transparent)

Each transition = PNG sequence `<name>/%04d.png` (RGBA, files start at 0001) + `<name>.mov` (ProRes 4444 with alpha, for CapCut on phone).
HTML sources: `src/<name>.html` (GSAP timeline paused, seeked per frame with `window.seek(t)`). Re-render: `node render.js [name]`, then `python3 to_rgba.py`, `python3 analyze.py`, `python3 build_mov_preview.py`.

`cut_frame` = 0-based frame index (file number = index + 1) that is fully opaque-covered and sits in the middle of the covered run. Put your clip cut on that frame. `covered` = every frame index where the whole screen is 100% covered (safe window for the cut, +/- 1 frame of slack).

| name | duration | frames | cut_frame | covered (0-based) | best use |
|---|---|---|---|---|---|
| navy_wipe | 0.60 s | 18 | 9 | 7-11 | Main topic changes, hook -> explanation, section starts. Premium default. |
| gold_light_sweep | 0.50 s | 15 | none (peak at 7) | never covers | Soft accent on a same-scene cut, before a stat/CTA, over a title reveal. Never hides the cut, so cut on frame 7 (peak glow). |
| whip_blur_mask | 0.40 s | 12 | 4 | 3-6 | Fast energetic cuts, list items, "next tip" beats. Only ~4 covered frames, so cut precisely. |
| circle_iris_gold | 0.60 s | 18 | 7 | 6-9 | Reveals: before/after, product/result, face-to-3D-anatomy. |
| split_bars | 0.70 s | 21 | 10 | 9-11 | Heavy chapter breaks, numbered steps, big claims. Most "cinematic". |
| particle_dissolve | 0.80 s | 24 | none (gold dust peaks ~frame 8-12) | never covers | Medical/3D reveals, organ/anatomy fade-ins. Cut anywhere around frame 10. |

Frame 0 and the last frame of every sequence are (almost) empty, so the overlay never pops.

## ffmpeg: apply a transition centred on a cut at time T (30 fps 1080x1920 video)

Set `T` (seconds, the cut moment in the main timeline) and `C` (cut_frame from the table; use 7 for gold_light_sweep, 10 for particle_dissolve). Start time `T0 = T - C/30`.

```bash
T=12.5; C=9; NAME=navy_wipe          # example: navy_wipe centred on a cut at 12.5 s
TR=$HOME/reel-toolkit/transitions
T0=$(python3 -c "print($T-$C/30)")
ffmpeg -i main.mp4 -framerate 30 -i $TR/$NAME/%04d.png \
  -filter_complex "[1:v]setpts=PTS-STARTPTS+$T0/TB[t];[0:v][t]overlay=format=auto:eof_action=pass,format=yuv420p" \
  -c:v libx264 -crf 16 -preset slow -c:a copy out.mp4
```

Same thing with the ProRes file (`-i $TR/$NAME.mov` instead of the PNG pair; no `-framerate` needed).
Equivalent with an explicit window (`enable`) if you prefer: add `:enable='between(t,$T0,$T0+N/30)'` to `overlay` (N = frames column).

The clip itself must already contain the cut at T (A before, B after); the transition only hides it. Tested: with T=1.0 and C=4 (whip_blur_mask) the screen is fully covered on output frames 29-34 and the cut frame 30 is inside that.

Several transitions in one pass: chain overlays, one `[k:v]setpts=...[tk]` per extra input and `[v0][t1]overlay...[v1];[v1][t2]overlay...`.

## Files
- `preview.mp4` - all 6 on a A/B test cut, 0.5 s gaps (A and B swap on the cut frame).
- `preview_sheet.png` - mid-frame of each, 6x1, 1620 px wide. `preview_phases.png` - 28% / mid / 72% of each.
- `cut_frames.json` - machine-readable cut frames and covered ranges.
