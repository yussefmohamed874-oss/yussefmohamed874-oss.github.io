import React from 'react';
import {useCurrentFrame, useVideoConfig, spring, interpolate, Sequence} from 'remotion';
import {C, FONT} from '../theme';
import {sec} from '../lib/time';
import type {Card} from '../lib/time';

// Navy info card with gold frame, gold tag and check items (matches the reference style).
const CardBody: React.FC<{title: string; items: string[]}> = ({title, items}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const p = spring({frame, fps, config: {damping: 18, stiffness: 120}});
  return (
    <div
      style={{
        position: 'absolute', left: 60, bottom: 260, width: 560, boxSizing: 'border-box',
        background: C.navy, border: `3px solid ${C.gold}`, borderRadius: 28,
        padding: '52px 40px 36px', color: C.white, fontFamily: FONT, direction: 'rtl',
        boxShadow: '0 18px 50px rgba(0,0,0,0.45)',
        opacity: interpolate(p, [0, 1], [0, 1]),
        transform: `translateX(${interpolate(p, [0, 1], [-60, 0])}px)`,
      }}
    >
      <div style={{
        position: 'absolute', top: -28, right: 40, background: C.gold, color: C.navy,
        fontWeight: 800, fontSize: 36, padding: '4px 30px', borderRadius: 16,
      }}>{title}</div>
      {items.map((it, i) => (
        <div key={i} style={{fontSize: 44, fontWeight: 700, margin: '14px 0', display: 'flex', gap: 16, alignItems: 'center'}}>
          <span style={{color: C.gold, fontSize: 40}}>✓</span>
          <span>{it}</span>
        </div>
      ))}
    </div>
  );
};

export const InfoCards: React.FC<{cards: Card[]}> = ({cards}) => (
  <>
    {cards.map((c, i) => (
      <Sequence key={i} from={sec(c.from)} durationInFrames={sec(c.to - c.from)}>
        <CardBody title={c.title} items={c.items} />
      </Sequence>
    ))}
  </>
);
