import React from 'react';
import {AbsoluteFill, OffthreadVideo, Sequence, staticFile} from 'remotion';
import {sec} from '../lib/time';
import type {Seg, Card, ClipCut} from '../lib/time';
import {Caption} from '../components/Caption';
import {InfoCards} from '../components/InfoCard';
import {CameraPush, Grade, GoldSweep, Backdrop} from '../components/Cinema';
import {Water3D} from '../components/Water3D';
import {C} from '../theme';

// Generic 9:16 Reel template. Every project only supplies props (clips, captions, cards, timings).
export type ReelProps = {
  totalSec: number;
  clips: ClipCut[];          // footage on the composition timeline
  captions: Seg[];           // word-timed text, already offset to composition time
  keywords: string[];        // words to highlight in gold
  cards: Card[];
  water3d?: {from: number; to: number};
  sweeps?: number[];         // seconds where a gold sweep transition fires
};

export const Reel: React.FC<ReelProps> = ({clips, captions, keywords, cards, water3d, sweeps = []}) => (
  <AbsoluteFill style={{backgroundColor: C.navyDeep}}>
    {clips.map((c, i) => (
      <Sequence key={i} from={sec(c.from)} durationInFrames={sec(c.to - c.from)}>
        <CameraPush frames={sec(c.to - c.from)}>
          <OffthreadVideo
            src={staticFile(c.src)}
            startFrom={sec(c.sourceStart ?? 0)}
            muted={false}
            style={{width: '100%', height: '100%', objectFit: 'cover'}}
          />
        </CameraPush>
      </Sequence>
    ))}

    {water3d && (
      <Sequence from={sec(water3d.from)} durationInFrames={sec(water3d.to - water3d.from)}>
        <Water3D />
      </Sequence>
    )}

    <Grade />
    <InfoCards cards={cards} />
    <Caption segments={captions} keywords={keywords} />
    {sweeps.map((s, i) => <GoldSweep key={i} start={sec(s)} />)}
  </AbsoluteFill>
);
