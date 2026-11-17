// Convert a montage-tools transcript (out/<name>.json from `mt transcribe`) into Caption segments,
// shifted by an offset (seconds) so it lines up with the composition timeline.
// usage: node scripts/whisper_to_captions.mjs <transcript.json> [offsetSec] > captions.json
import {readFileSync} from 'node:fs';
const [, , file, offsetArg = '0'] = process.argv;
const off = Number(offsetArg);
const d = JSON.parse(readFileSync(file, 'utf8'));
const r = (x) => Math.round(x * 1000) / 1000;
const segments = d.segments.map((s) => ({
  start: r(s.start + off), end: r(s.end + off), text: s.text,
  words: s.words.map((w) => ({word: w.word, start: r(w.start + off), end: r(w.end + off)})),
}));
process.stdout.write(JSON.stringify(segments, null, 1));
