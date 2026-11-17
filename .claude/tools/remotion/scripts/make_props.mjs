// Build a Reel props file: node scripts/make_props.mjs <out.json> <totalSec> <captions.json> <clipSrc:clipDur>...
import {writeFileSync, readFileSync} from 'node:fs';
const [, , out, total, capFile, ...clipArgs] = process.argv;
let t = 0;
const clips = clipArgs.map((a) => {
  const [src, dur] = a.split(':'); const d = Number(dur);
  const c = {src, from: t, to: t + d, sourceStart: 0}; t += d; return c;
});
const props = {
  totalSec: Number(total), clips,
  captions: JSON.parse(readFileSync(capFile, 'utf8')),
  keywords: [], cards: [], sweeps: [],
};
writeFileSync(out, JSON.stringify(props, null, 1));
console.log('wrote', out);
