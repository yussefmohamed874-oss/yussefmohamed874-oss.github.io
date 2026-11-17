import React from 'react';
import {useCurrentFrame, spring, useVideoConfig, interpolate} from 'remotion';
import {C, FONT, FPS, W} from '../theme';
import type {Seg} from '../lib/time';

const norm = (s: string) => s.replace(/[ً-ْـ]/g, '').replace(/[^؀-ۿA-Za-z0-9]/g, '');

// Word-synced Arabic caption. Words light up as they are spoken; keywords are gold.
export const Caption: React.FC<{
  segments: Seg[];
  keywords?: string[];
  y?: number;
}> = ({segments, keywords = [], y = 1180}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / FPS;
  const seg = segments.find((s) => t >= s.start - 0.1 && t <= s.end + 0.35);
  if (!seg) return null;

  const enter = spring({frame: frame - Math.round(seg.start * FPS), fps, config: {damping: 200}});
  const kw = new Set(keywords.map(norm));

  return (
    <div
      style={{
        position: 'absolute', left: 60, right: 60, top: y, direction: 'rtl',
        display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: '0 18px',
        fontFamily: FONT, fontWeight: 800, fontSize: 84, lineHeight: 1.35, textAlign: 'center',
        opacity: interpolate(enter, [0, 1], [0, 1]),
        transform: `translateY(${interpolate(enter, [0, 1], [24, 0])}px)`,
        textShadow: '0 6px 22px rgba(0,0,0,0.65)',
        width: W - 120,
      }}
    >
      {seg.words.map((w, i) => {
        const spoken = t >= w.start;
        const isKw = kw.has(norm(w.word));
        return (
          <span
            key={i}
            style={{
              color: isKw ? C.gold : C.white,
              opacity: spoken ? 1 : 0.4,
            }}
          >
            {w.word}
          </span>
        );
      })}
    </div>
  );
};
