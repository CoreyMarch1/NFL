import React from 'react';
import {Composition} from 'remotion';
import {DURATION, FPS, HEIGHT, WIDTH} from './config';
import {Teaser} from './Teaser';

export const Root: React.FC = () => (
  <Composition id="Teaser" component={Teaser} durationInFrames={DURATION} fps={FPS} width={WIDTH} height={HEIGHT} />
);
