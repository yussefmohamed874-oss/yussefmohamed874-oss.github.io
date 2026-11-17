import React from 'react';
import {useCurrentFrame, interpolate, AbsoluteFill, Easing} from 'remotion';
import {ThreeCanvas} from '@remotion/three';
import {C, W, H} from '../theme';

// 3D water droplet with a gold ring. Rendered with Three.js through React Three Fiber.
const Droplet: React.FC = () => {
  const f = useCurrentFrame();
  const spin = f * 0.02;
  const bob = Math.sin(f / 18) * 0.12;
  return (
    <>
      <ambientLight intensity={0.5} />
      <directionalLight position={[3, 4, 5]} intensity={1.6} color="#ffffff" />
      <pointLight position={[-3, -2, 3]} intensity={1.2} color={C.gold} />
      <group position={[0, bob, 0]} rotation={[0, spin, 0]}>
        <mesh scale={[1, 1.25, 1]}>
          <sphereGeometry args={[1, 64, 64]} />
          <meshPhysicalMaterial color="#7fb8ff" transmission={0.6} roughness={0.08} thickness={1.2} clearcoat={1} />
        </mesh>
      </group>
      <mesh rotation={[Math.PI / 2.4, 0, 0]} position={[0, -1.2, 0]}>
        <torusGeometry args={[1.7, 0.02, 16, 120]} />
        <meshStandardMaterial color={C.gold} emissive={C.gold} emissiveIntensity={0.6} />
      </mesh>
    </>
  );
};

export const Water3D: React.FC = () => {
  const f = useCurrentFrame();
  const fadeIn = interpolate(f, [0, 12], [0, 1], {easing: Easing.out(Easing.quad), extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{opacity: fadeIn}}>
      <AbsoluteFill style={{background: `radial-gradient(circle at 50% 45%, #13305f 0%, ${C.navyDeep} 75%)`}} />
      <ThreeCanvas width={W} height={H} camera={{position: [0, 0, 5.2], fov: 38}}>
        <Droplet />
      </ThreeCanvas>
    </AbsoluteFill>
  );
};
