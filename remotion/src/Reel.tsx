import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';

export const Reel = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const scale = spring({frame, fps, config: {damping: 12}});
  const opacity = interpolate(frame, [0, 20], [0, 1], {extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{background: 'linear-gradient(160deg,#0f172a,#1e3a5f)', justifyContent: 'center', alignItems: 'center'}}>
      <h1 style={{color: '#fff', fontSize: 120, fontFamily: 'sans-serif', direction: 'rtl', textAlign: 'center', transform: `scale(${scale})`, opacity}}>
        رسام الرشاقة
      </h1>
    </AbsoluteFill>
  );
};
