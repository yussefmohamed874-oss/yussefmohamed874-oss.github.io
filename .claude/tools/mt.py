#!/usr/bin/env python3
"""montage-tools: probe / extract / transcribe / silence / cuts / apply.

Never modifies originals. All outputs go to work/ or out/.
Timestamps always refer to the ORIGINAL media timeline until `apply`
writes remapped files (*.edit.*).
"""
import argparse, json, os, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MODEL_DIR = ROOT / "models" / "whisper-small-ct2-int8"
WORK = ROOT / "work"
OUT = ROOT / "out"


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def stem(p):
    return Path(p).stem


def srt_time(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


# ---------------------------------------------------------------- probe
def cmd_probe(a):
    r = run(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", a.input])
    d = json.loads(r.stdout)
    out = {"duration": float(d["format"]["duration"]), "streams": []}
    for s in d["streams"]:
        out["streams"].append({k: s.get(k) for k in
            ("index", "codec_type", "codec_name", "width", "height", "r_frame_rate",
             "sample_rate", "channels", "duration")})
    print(json.dumps(out, indent=2, ensure_ascii=False))


# ---------------------------------------------------------------- extract
def cmd_extract(a):
    WORK.mkdir(exist_ok=True)
    out = WORK / f"{stem(a.input)}.wav"
    # 16 kHz mono PCM, no trimming -> timestamps == original timeline
    r = run(["ffmpeg", "-y", "-v", "error", "-i", a.input, "-vn", "-ac", "1", "-ar", "16000",
             "-c:a", "pcm_s16le", str(out)])
    if r.returncode: sys.exit(r.stderr)
    print(out)


# ---------------------------------------------------------------- transcribe
def cmd_transcribe(a):
    from faster_whisper import WhisperModel
    wav = WORK / f"{stem(a.input)}.wav"
    if not wav.exists():
        cmd_extract(a)
    model = WhisperModel(str(MODEL_DIR), device="cpu", compute_type="int8",
                         cpu_threads=os.cpu_count() or 4)
    segs, info = model.transcribe(str(wav), language=a.lang, beam_size=5,
                                  word_timestamps=True, vad_filter=False,
                                  condition_on_previous_text=False,
                                  initial_prompt=a.prompt)
    data = {"source": str(Path(a.input).resolve()), "language": info.language,
            "duration": info.duration, "model": "whisper-small (ct2 int8)", "segments": []}
    for s in segs:
        data["segments"].append({
            "start": round(s.start, 3), "end": round(s.end, 3), "text": s.text.strip(),
            "words": [{"word": w.word.strip(), "start": round(w.start, 3),
                       "end": round(w.end, 3), "prob": round(w.probability, 3)}
                      for w in (s.words or [])]})
    OUT.mkdir(exist_ok=True)
    base = OUT / stem(a.input)
    base.with_suffix(".json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    base.with_suffix(".txt").write_text("\n".join(s["text"] for s in data["segments"]) + "\n", encoding="utf-8")
    write_srt(base.with_suffix(".srt"), data["segments"])
    print(f"{base}.json/.txt/.srt  ({len(data['segments'])} segments)")


def write_srt(path, segments):
    with open(path, "w", encoding="utf-8") as f:
        for i, s in enumerate(segments, 1):
            f.write(f"{i}\n{srt_time(s['start'])} --> {srt_time(s['end'])}\n{s['text']}\n\n")


# ---------------------------------------------------------------- silence
def detect_silence(path, noise_db, min_dur):
    r = run(["ffmpeg", "-v", "info", "-i", path, "-vn", "-af",
             f"silencedetect=noise={noise_db}dB:d={min_dur}", "-f", "null", "-"])
    starts = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", r.stderr)]
    ends = [(float(e), float(d)) for e, d in re.findall(r"silence_end: ([\d.]+) \| silence_duration: ([\d.]+)", r.stderr)]
    res = []
    for i, st in enumerate(starts):
        if i < len(ends):
            res.append({"start": max(0, st), "end": ends[i][0], "dur": ends[i][1]})
        else:  # silence runs to end of file
            res.append({"start": max(0, st), "end": None, "dur": None})
    return res


def cmd_silence(a):
    OUT.mkdir(exist_ok=True)
    sil = detect_silence(a.input, a.noise, a.min)
    p = OUT / f"{stem(a.input)}.silence.json"
    p.write_text(json.dumps(sil, indent=2))
    print(f"{len(sil)} silent spans -> {p}")
    for s in sil:
        print(f"  {s['start']:.2f} -> {s['end'] if s['end'] is None else round(s['end'], 2)}  ({s['dur']})")


# ---------------------------------------------------------------- cuts
def duration(path):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path])
    return float(r.stdout.strip())


def cmd_cuts(a):
    """Propose cuts. Primary signal = real silence (ffmpeg silencedetect, min length --max-pause).
    Each span is shrunk by max(--pad, --keep/2) per side so natural pauses and word edges survive;
    spans that touch a transcribed word are dropped. Lead-in/tail keep --lead/--tail seconds."""
    dur = duration(a.input)
    tj = OUT / f"{stem(a.input)}.json"
    words = []
    if tj.exists() and not a.no_words:
        words = [w for s in json.loads(tj.read_text(encoding="utf-8"))["segments"] for w in s["words"]]
    m = max(a.pad, a.keep / 2)
    remove = []
    for s in detect_silence(a.input, a.noise, a.max_pause):
        end = s["end"] if s["end"] is not None else dur
        if s["start"] <= 0.01:
            s0, e0 = 0.0, end - a.lead                       # lead-in
        elif end >= dur - 0.02:
            s0, e0 = s["start"] + a.tail, dur                # tail
        else:
            s0, e0 = s["start"] + m, end - m
        if e0 - s0 < 0.05:
            continue
        clash = [w for w in words if w["end"] > s0 + 0.03 and w["start"] < e0 - 0.03 and w["start"] > 0.05]
        if clash:
            continue
        remove.append((s0, e0))
    basis = "silencedetect+words" if words else "silencedetect"
    keep, t = [], 0.0
    for s0, e0 in sorted(remove):
        if s0 > t: keep.append([round(t, 3), round(s0, 3)])
        t = max(t, e0)
    if t < dur - 0.001: keep.append([round(t, 3), round(dur, 3)])
    proposal = {"source": str(Path(a.input).resolve()), "basis": basis, "duration": dur,
                "params": {k: getattr(a, k) for k in ("max_pause", "keep", "pad", "lead", "tail", "noise")},
                "remove": [[round(s, 3), round(e, 3)] for s, e in sorted(remove)],
                "keep": keep,
                "saved_seconds": round(sum(e - s for s, e in remove), 3),
                "approved": False}
    OUT.mkdir(exist_ok=True)
    p = OUT / f"{stem(a.input)}.cuts.json"
    p.write_text(json.dumps(proposal, indent=2))
    print(f"{p}\nbasis={basis} remove={len(remove)} spans, saves {proposal['saved_seconds']}s of {dur:.2f}s")
    for s, e in proposal["remove"]:
        print(f"  cut {s:.2f} -> {e:.2f} ({e - s:.2f}s)")
    print("Review, then set \"approved\": true and run `mt apply`.")


# ---------------------------------------------------------------- apply
def cmd_apply(a):
    cj = json.loads(Path(a.cuts).read_text())
    if not cj.get("approved") and not a.force:
        sys.exit("cuts file is not approved (set \"approved\": true after review, or pass --force)")
    src = cj["source"]
    keep = cj["keep"]
    fade = a.fade
    vf, af, labels = [], [], ""
    for i, (s, e) in enumerate(keep):
        vf.append(f"[0:v]trim=start={s}:end={e},setpts=PTS-STARTPTS[v{i}]")
        d = e - s
        f = min(fade, d / 2)
        af.append(f"[0:a]atrim=start={s}:end={e},asetpts=PTS-STARTPTS,"
                  f"afade=t=in:d={f},afade=t=out:st={max(0, d - f):.4f}:d={f}[a{i}]")
        labels += f"[v{i}][a{i}]"
    fc = ";".join(vf + af) + f";{labels}concat=n={len(keep)}:v=1:a=1[v][a]"
    WORK.mkdir(exist_ok=True)
    out = WORK / f"{stem(src)}.edit.mp4"
    r = run(["ffmpeg", "-y", "-v", "error", "-i", src, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
             "-c:v", "libx264", "-crf", str(a.crf), "-preset", "medium", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out)])
    if r.returncode: sys.exit(r.stderr)
    # remap transcript to the edited timeline
    tj = OUT / f"{stem(src)}.json"
    if tj.exists():
        data = json.loads(tj.read_text(encoding="utf-8"))
        total = sum(e - s for s, e in keep)
        def remap(t):
            acc = 0.0
            for s, e in keep:
                if t < s: return round(acc, 3), True      # inside a cut -> snap to next kept edge
                if t <= e: return round(acc + t - s, 3), False
                acc += e - s
            return round(total, 3), True
        segs = []
        for sg in data["segments"]:
            ws = []
            for w in sg["words"]:
                (s2, f1), (e2, f2) = remap(w["start"]), remap(w["end"])
                nw = dict(w, start=s2, end=max(e2, s2))
                if f1 or f2: nw["snapped"] = True
                ws.append(nw)
            if ws:
                segs.append({"start": ws[0]["start"], "end": ws[-1]["end"], "text": sg["text"], "words": ws})
        data["segments"] = segs; data["duration"] = duration(str(out)); data["source"] = str(out)
        (OUT / f"{stem(src)}.edit.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        write_srt(OUT / f"{stem(src)}.edit.srt", segs)
    print(f"{out}  {duration(src):.2f}s -> {duration(str(out)):.2f}s")


def main():
    ap = argparse.ArgumentParser(prog="mt")
    sp = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in (("probe", cmd_probe), ("extract", cmd_extract), ("transcribe", cmd_transcribe),
                     ("silence", cmd_silence), ("cuts", cmd_cuts)):
        p = sp.add_parser(name); p.add_argument("input"); p.set_defaults(fn=fn)
        if name == "transcribe":
            p.add_argument("--lang", default="ar"); p.add_argument("--prompt", default=None)
        if name in ("silence", "cuts"):
            p.add_argument("--noise", type=float, default=-35)
        if name == "silence":
            p.add_argument("--min", type=float, default=0.4)
        if name == "cuts":
            p.add_argument("--max-pause", type=float, default=0.5, dest="max_pause")
            p.add_argument("--keep", type=float, default=0.4, help="pause length left after a cut")
            p.add_argument("--pad", type=float, default=0.12, help="safety margin around words")
            p.add_argument("--lead", type=float, default=0.15); p.add_argument("--tail", type=float, default=0.3)
            p.add_argument("--no-words", action="store_true")
    p = sp.add_parser("apply"); p.add_argument("cuts"); p.set_defaults(fn=cmd_apply)
    p.add_argument("--crf", type=int, default=16); p.add_argument("--fade", type=float, default=0.012)
    p.add_argument("--force", action="store_true")
    a = ap.parse_args(); a.fn(a)


if __name__ == "__main__":
    main()
