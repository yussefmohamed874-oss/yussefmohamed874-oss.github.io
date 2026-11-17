import React from 'react';
import {useCurrentFrame, interpolate, AbsoluteFill, Easing} from 'remotion';
import {C} from '../theme';

// Slow push-in on the whole scene (depth without shaky handheld).
export const CameraPush: React.FC<{from?: number; to?: number; frames: number; children: React.ReactNode}> = ({
  from = 1, to = 1.06, frames, children,
}) => {
  const f = useCurrentFrame();
  const s = interpolate(f, [0, Math.max(1, frames)], [from, to], {
    extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic),
  });
  return <AbsoluteFill style={{transform: `scale(${s})`}}>{children}</AbsoluteFill>;
};

// Grade: navy shadows, warm gold highlights, vignette. Applied on top of footage.
export const Grade: React.FC<{strength?: number}> = ({strength = 1}) => (
  <AbsoluteFill style={{pointerEvents: 'none'}}>
    <AbsoluteFill style={{background: `linear-gradient(180deg, rgba(6,14,34,${0.25 * strength}) 0%, rgba(6,14,34,0) 45%, rgba(6,14,34,${0.45 * strength}) 100%)`, mixBlendMode: 'multiply'}} />
    <AbsoluteFill style={{background: `rgba(216,169,59,${0.07 * strength})`, mixBlendMode: 'soft-light'}} />
    <AbsoluteFill style={{background: 'radial-gradient(ellipse at center, rgba(0,0,0,0) 55%, rgba(0,0,0,0.55) 100%)'}} />
  </AbsoluteFill>
);

// Gold light sweep used as a cinematic transition between scenes.
export const GoldSweep: React.FC<{start: number; frames?: number}> = ({start, frames = 14}) => {
  const f = useCurrentFrame() - start;
  if (f < 0 || f > frames) return null;
  const x = interpolate(f, [0, frames], [-1100, 1100], {easing: Easing.out(Easing.quad)});
  return (
    <AbsoluteFill style={{pointerEvents: 'none', overflow: 'hidden'}}>
      <div style={{
        position: 'absolute', top: -200, bottom: -200, left: '50%', width: 520,
        transform: `translateX(${x}px) skewX(-12deg)`,
        background: `linear-gradient(90deg, rgba(216,169,59,0) 0%, rgba(242,210,122,0.55) 50%, rgba(216,169,59,0) 100%)`,
        mixBlendMode: 'screen',
      }} />
    </AbsoluteFill>
  );
};

export const Backdrop: React.FC = () => (
  <AbsoluteFill style={{background: `radial-gradient(circle at 50% 35%, ${C.navy} 0%, ${C.navyDeep} 70%)`}} />
);
