import React from 'react';
import {Freeze, OffthreadVideo, continueRender, delayRender, staticFile} from 'remotion';
import {ASSETS, Rect, SEASON_TABLE} from '../config';

export const PIXEL_FONT = 'OADPixel';
export const MONO_FONT = 'OADMono';

// Fonts are bundled locally in assets/fonts and loaded before any frame renders.
if (typeof document !== 'undefined') {
  const handle = delayRender('fonts');
  const faces = [
    new FontFace(PIXEL_FONT, `url(${staticFile(ASSETS.fontPixel)})`),
    new FontFace(MONO_FONT, `url(${staticFile(ASSETS.fontMono)})`, {weight: '700'}),
  ];
  Promise.all(faces.map((f) => f.load()))
    .then((loaded) => {
      loaded.forEach((f) => document.fonts.add(f));
      continueRender(handle);
    })
    .catch((e) => {
      console.error('font load failed', e);
      continueRender(handle);
    });
}

export const clamp01 = (v: number) => Math.max(0, Math.min(1, v));
export const prog = (frame: number, from: number, to: number) => clamp01((frame - from) / (to - from));
export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
export const easeOut = (t: number) => 1 - Math.pow(1 - t, 3);
export const easeInOut = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
export const lerpRect = (a: Rect, b: Rect, t: number): Rect => ({
  x: lerp(a.x, b.x, t),
  y: lerp(a.y, b.y, t),
  w: lerp(a.w, b.w, t),
  h: lerp(a.h, b.h, t),
});

// Deterministic pseudo-random number in [0,1) from a frame number.
export const hash = (n: number, salt = 0) => {
  const x = Math.sin(n * 127.1 + salt * 311.7) * 43758.5453;
  return x - Math.floor(x);
};

// Shows one exact source frame of a prepped recording. The frame shown is a
// pure function of `sourceFrame`, so all video motion is frame-number driven.
export const Clip: React.FC<{src: string; sourceFrame: number; style?: React.CSSProperties}> = ({
  src,
  sourceFrame,
  style,
}) => (
  <Freeze frame={Math.max(0, Math.round(sourceFrame))}>
    <OffthreadVideo
      src={staticFile(src)}
      muted
      style={{position: 'absolute', left: 0, top: 0, width: ASSETS.clipSize.w, height: ASSETS.clipSize.h, ...style}}
    />
  </Freeze>
);

// A camera window onto source-pixel space: children are positioned in source
// pixels, and the rectangle `win` is scaled to fill outW x outH.
export const Window: React.FC<{
  win: {x: number; y: number; w: number};
  outW: number;
  outH: number;
  children: React.ReactNode;
  background?: string;
}> = ({win, outW, outH, children, background}) => {
  const s = outW / win.w;
  return (
    <div style={{position: 'absolute', left: 0, top: 0, width: outW, height: outH, overflow: 'hidden', background}}>
      <div
        style={{
          position: 'absolute',
          left: 0,
          top: 0,
          transformOrigin: '0 0',
          transform: `scale(${s}) translate(${-win.x}px, ${-win.y}px)`,
        }}
      >
        {children}
      </div>
    </div>
  );
};

export const Box: React.FC<{r: Rect; style?: React.CSSProperties; children?: React.ReactNode}> = ({
  r,
  style,
  children,
}) => (
  <div style={{position: 'absolute', left: r.x, top: r.y, width: r.w, height: r.h, ...style}}>{children}</div>
);

// The season table with the empty middle of each row closed up: two strips of
// the roadmap recording side by side. `top` is the source y at the top edge.
export const SeasonTable: React.FC<{sourceFrame: number; top: number; height: number}> = ({sourceFrame, top, height}) => {
  let left = 0;
  return (
    <>
      {SEASON_TABLE.strips.map((st) => {
        const x = left;
        left += st.w;
        return (
          <div key={st.x} style={{position: 'absolute', left: x, top: 0, width: st.w + 0.5, height, overflow: 'hidden'}}>
            <Clip src={ASSETS.roadmap} sourceFrame={sourceFrame} style={{left: -st.x, top: -top}} />
          </div>
        );
      })}
    </>
  );
};
// source x -> x inside the two-strip table
export const tableX = (x: number) => {
  let left = 0;
  for (const st of SEASON_TABLE.strips) {
    if (x >= st.x && x <= st.x + st.w) return left + (x - st.x);
    left += st.w;
  }
  return x;
};
