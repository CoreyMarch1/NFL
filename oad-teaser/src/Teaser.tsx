import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {CUTS} from './config';
import {Supers} from './components/Super';
import {Shot1, Shot2, Shot6} from './shots/CabinetShots';
import {Shot3, Shot4, Shot5} from './shots/FullShots';

export const Teaser: React.FC = () => {
  const frame = useCurrentFrame();
  let shot: React.ReactNode;
  if (frame < CUTS.shot2) shot = <Shot1 frame={frame} />;
  else if (frame < CUTS.shot3) shot = <Shot2 frame={frame} />;
  else if (frame < CUTS.shot4) shot = <Shot3 frame={frame} />;
  else if (frame < CUTS.shot5) shot = <Shot4 frame={frame} />;
  else if (frame < CUTS.shot6) shot = <Shot5 frame={frame} />;
  else shot = <Shot6 frame={frame} />;
  return (
    <AbsoluteFill style={{background: '#000'}}>
      {shot}
      <Supers frame={frame} />
    </AbsoluteFill>
  );
};
