#!/usr/bin/env bash
# Reel toolkit presets for Dr. Youssef El Masry. Source this file: `. presets.sh`

# ---------- Lighting / color (speaker footage only) ----------
# Measured on the insulin-resistance raw (8-bit bt709 HEVC): frame p50 ~165 (bright grey wall), p99 220, no clipping,
# face p50 ~130-150, skin B/R 0.65-0.68 (slightly warm, OK). Problem = bright flat wall stealing attention, low depth.
GRADE_SOFT="curves=master='0/0.01 0.25/0.22 0.5/0.47 0.8/0.76 1/0.93',colorbalance=bm=0.03:rh=-0.02:bh=0.03,eq=contrast=1.06:saturation=1.0"
GRADE_CINEMATIC="curves=master='0/0.01 0.25/0.21 0.5/0.46 0.8/0.74 1/0.9',colorbalance=bs=0.04:bm=0.03:rh=-0.025:bh=0.04,eq=contrast=1.08:saturation=0.97,vignette=angle=PI/5:mode=forward"
# For overexposed / yellow footage (from the enhancer skill):
GRADE_FIX_YELLOW="curves=master='0/0.02 0.2/0.17 0.5/0.44 0.8/0.74 0.93/0.87 1/0.95',colorbalance=rm=-0.045:bm=0.06:rh=-0.03:bh=0.045,selectivecolor=yellows='0 0 -0.2 0':reds='0 0 -0.08 0',eq=saturation=0.9:contrast=1.05"

# ---------- Framing ----------
PUNCH_100="scale=1080:1920"
PUNCH_112="scale=1210:2150,crop=1080:1920:(iw-1080)/2:(ih-1920)/2-60"   # keeps face high
PUNCH_125="scale=1350:2400,crop=1080:1920:(iw-1080)/2:(ih-1920)/2-120"  # emphasis close-up

# ---------- Voice chain (lav mic, no denoise) ----------
# Insulin-resistance raw: clips range -13.5 to -15.8 LUFS, LRA 0.8-6 LU, peaks ~0 dBFS but only 2 peak samples
# (phone already limited, not clipped). => match each clip to -15 LUFS with constant gain BEFORE concat,
# keep compression light (ratio 2) because the source is already dense.
VOICE_CHAIN="highpass=f=70,equalizer=f=220:t=q:w=1.2:g=-1.2,equalizer=f=3200:t=q:w=1:g=1.2,deesser=i=0.35,acompressor=threshold=-20dB:ratio=2:attack=8:release=120"
MUSIC_BED_GAIN="volume=0.11"
DUCK="sidechaincompress=threshold=0.03:ratio=8:attack=20:release=300"   # [music][voice]sidechaincompress
FINAL_LIMIT="alimiter=limit=0.891:level=disabled"                        # -1 dBTP
# Final loudness: measure with ebur128, then apply constant gain = (-14 - I) dB before FINAL_LIMIT.

# ---------- Transitions (ffmpeg xfade; use sparingly, never the same one twice in a row) ----------
# Hard cut + punch-in is the default. Inserts: 0.14 s alpha fade in/out (L-cut, voice continues).
XF_FADE_BLACK="fadeblack"     # section break
XF_SMOOTH_UP="smoothup"       # into a list / card
XF_SLIDE_LEFT="slideleft"     # fast topic change
XF_CIRCLE="circleopen"        # reveal of a 3D medical shot
XF_ZOOM="zoomin"              # emphasis into close detail
XF_DISSOLVE="dissolve"        # calm moments
XF_WIPE_TL="wipetl"           # diagonal brand wipe
# Custom brand transitions are rendered in Chromium (transitions/*.html): navy panel wipe with gold edge,
# gold light sweep, whip-blur. Overlay them as transparent PNG sequences on the cut point.

# ---------- Export ----------
EXPORT_V="-c:v libx264 -crf 17 -preset medium -pix_fmt yuv420p -r 30 -movflags +faststart"
EXPORT_A="-c:a aac -b:a 256k -ar 48000"
