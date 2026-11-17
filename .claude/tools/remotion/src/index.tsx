import React from 'react';
import {registerRoot, Composition} from 'remotion';
import '@fontsource/cairo/400.css';
import '@fontsource/cairo/700.css';
import '@fontsource/cairo/800.css';
import {Reel, ReelProps} from './templates/Reel';
import {W, H, FPS, C} from './theme';
import {sec} from './lib/time';
import testData from './data/test.json';

const Root: React.FC = () => (
  <Composition<React.FC<ReelProps>, ReelProps>
    id="Reel"
    component={Reel as any}
    width={W}
    height={H}
    fps={FPS}
    durationInFrames={sec(testData.totalSec)}
    defaultProps={testData as ReelProps}
    calculateMetadata={({props}) => ({durationInFrames: sec(props.totalSec)})}
  />
);

registerRoot(Root);
export {C};
